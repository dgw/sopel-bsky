"""sopel-bsky

Fetch info about Bluesky links in your IRC conversations using Sopel.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
import threading
import time

from sopel import plugin
from sopel.config.types import (
    NO_DEFAULT,
    SecretAttribute,
    StaticSection,
    ValidatedAttribute,
)
from sopel.tools import time as tools_time


def _parse_iso_datetime(timestamp: str) -> datetime:
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


class BskySection(StaticSection):
    handle = ValidatedAttribute('handle', default=NO_DEFAULT)
    password = SecretAttribute('password', default=NO_DEFAULT)
    newline_replacement = ValidatedAttribute(
        'newline_replacement',
        default='⏎',
    )


def configure(config):
    config.define_section('bsky', BskySection, validate=False)
    config.bsky.configure_setting(
        'handle',
        'Bluesky account handle:',
    )
    config.bsky.configure_setting(
        'password',
        'Bluesky account password:',
    )
    config.bsky.configure_setting(
        'newline_replacement',
        'Replacement character(s) for newlines in skeet text '
        '(default: "⏎"; enter "off" to disable):',
    )


def setup(bot):
    bot.memory['bsky_client'] = None

    bot.config.define_section('bsky', BskySection)
    settings = bot.config.bsky

    def initialize_bsky_client():
        import atproto  # done here to avoid slowing down the initial plugin load

        client = atproto.Client()
        client.login(settings.handle, settings.password)
        bot.memory['bsky_client'] = client

    # Start client initialization in a background thread;
    # let Sopel continue loading other plugins
    bot.memory['bsky_client_init_thread'] = threading.Thread(
        target=initialize_bsky_client, daemon=True)
    bot.memory['bsky_client_init_thread'].start()


def shutdown(bot):
    if 'bsky_client_init_thread' in bot.memory:
        if (init_thread := bot.memory['bsky_client_init_thread']) and init_thread.is_alive():
            init_thread.join(timeout=5)
        del bot.memory['bsky_client_init_thread']


@plugin.output_prefix('[skeet] ')
@plugin.url(
    r'https?://bsky\.app/profile/(?P<actor>[^/]+)/post/(?P<post_id>[^/]+)')
def skeet_info(bot, trigger):
    while not (client := bot.memory['bsky_client']):
        time.sleep(1)

    actor = trigger.group('actor')
    post = client.get_post(trigger.group('post_id'), actor)
    profile = client.get_profile(actor)

    now = trigger.time
    then = _parse_iso_datetime(post.value.created_at)
    timediff = (now - then).total_seconds()

    template = '{name} (@{handle}) | {reltime} | {text}'
    newline_repl = bot.config.bsky.newline_replacement.strip()
    if '\n' in (text := post.value.text) and newline_repl.lower() != 'off':
        # I thought this was a micro-optimization, but testing with `timeit`
        # shows that `in` is about 2 OOM faster than running the substitution if
        # it's not needed:
        #
        # >>> timeit('"\\n" in s', 's = "\\n"')
        # 0.022922827000002144
        # >>> timeit('"\\n" in s', 's = "\\n"*1000')
        # 0.03323874300076568
        # >>> timeit('re.sub("\\n+", "f", s)', 'import re; s = "\\n"*1000')
        # 1.3035988219999126
        # >>> # the most damning one, where there are no newlines at all
        # >>> timeit('re.sub("\\n+", "f", s)', 'import re; s = "n"*1000')
        # 9.526578507999147
        #
        # So yeah, this optimization isn't *that* "micro" after all.
        text = re.sub(
            r'(?:\s+)?\n+',  # match trailing space before newlines too, if any
            f' {newline_repl} ',
            text,
        )

    bot.say(
        template.format(
            name=profile.display_name,
            handle=profile.handle,
            reltime=tools_time.seconds_to_human(timediff),
            text=text,
        ),
        truncation=' […]',
    )


@plugin.output_prefix('[skeeter] ')
@plugin.url(
    r'https?://bsky.app/profile/(?P<handle>[^/]+)$')
def skeeter_info(bot, trigger):
    while not (client := bot.memory['bsky_client']):
        time.sleep(1)

    profile = client.get_profile(trigger.group('handle'))
    template = (
        '{name} (@{handle}) | Following {following} | Followed by {followers}'
        ' | {skeets} skeets | {bio}'
    )
    bot.say(
        template.format(
            name=profile.display_name,
            handle=profile.handle,
            following=profile.follows_count,
            followers=profile.followers_count,
            skeets=profile.posts_count,
            bio=profile.description,
        ),
        truncation=' […]',
    )
