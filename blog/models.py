from datetime import datetime
import re, urllib, functools
from flask import (Flask, abort, flash, Markup, redirect, render_template,
                   request, Response, session, url_for)
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *
from blog import flask_db, database, oembed_providers, blog


class Post(flask_db.Model):
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    timestamp = DateTimeField(default=datetime.now, index=True)
    image = CharField(default='')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
        ret = super(Post, self).save(*args, **kwargs)

        # Store search content.
        self.update_search_index()
        return ret

    def update_search_index(self):
        try:
            fts_entry = FTSPost.get(FTSPost.entry_id == self.id)
        except FTSPost.DoesNotExist:
            fts_entry = FTSPost(entry_id=self.id)
            force_insert = True
        else:
            force_insert = False
        fts_entry.content = '\n'.join((self.title, self.content))
        fts_entry.save(force_insert=force_insert)

    @classmethod
    def public(cls):
        return Post.select().where(Post.published == True)

    @classmethod
    def drafts(cls):
        return Post.select().where(Post.published == False)

    @classmethod
    def search(cls, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return empty query.
            return Post.select().where(Post.id == 0)
        else:
            search = ' '.join(words)

        return (FTSPost
                .select(
            FTSPost,
            Post,
            FTSPost.rank().alias('score'))
                .join(Post, on=(FTSPost.entry_id == Post.id).alias('post'))
                .where(
            (Post.published == True) &
            (FTSPost.match(search)))
                .order_by(SQL('score').desc()))

    @property
    def html_content(self):
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=blog.config['SITE_WIDTH'])
        return Markup(oembed_content)


class FTSPost(FTSModel):
    entry_id = IntegerField()
    content = TextField()

    class Meta:
        database = database