# sopel-bsky

Fetch info about Bluesky links in your IRC conversations using Sopel.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-bsky
```

Please note that the `atproto` package maintains a strict Python version policy,
so installation might not be possible on a given Python release even if Sopel
itself is compatible with it. Drop by [GitHub][gh-sopel-bsky] and open a PR or
issue if you notice that the dependencies are outdated.

[gh-sopel-bsky]: https://github.com/sopel-irc/sopel-bsky

## Configuring

The easiest way to configure `sopel-bsky` is via Sopel's configuration
wizard—simply run `sopel-plugins configure bsky` and enter the values for which
it prompts you.

### Account login

At present, you need to give the plugin a Bluesky account for which you don't
mind storing the `handle` & `password` in Sopel's config file in plain text.
It's recommended to create a new account specifically for your bot, instead of
using your real account's credentials (if you have one).

### Output behavior

These settings control how `sopel-bsky` displays skeet contents.

#### `newline_replacement`

_Default value:_ `"⏎"`

Runs of one or more newlines in a skeet's text will be replaced with this
string, wrapped in spaces. [For example][wilw-newline-test], the default value
of `⏎` is used like this:

```
<Sopel> [skeet] Wil Wheaton (@wilwheaton.net) | 6 hours, 28 minutes ago |
        Ranking Star Wars movies is a thing? ⏎ Okay, I'll get in on this. ⏎ 1.
        Empire Strikes Back ⏎ 2. Star Wars 1977 theatrical release ⏎ 3. Rogue
        One ⏎ 4. Return of the Jedi (because I was 11) ⏎ Everything else is
        somewhere between "meh" and "why. why. y u do dis?" [sad kitten dot jpg]
```

The special value `off` will disable newline substitution. Note that leading &
trailing spaces in the value you enter will be ignored; this is a limitation of
Sopel's config format and parser.

[wilw-newline-test]: https://bsky.app/profile/wilwheaton.net/post/3m6iac7rms22v

## Maintenance Note

This plugin as it exists now is mostly a proof of concept, just to have some
minimal level of parity with the Sopel ecosystem's support for Twitter (it is
_not_ called X!) and Mastodon.

Showing details for links to Bluesky users and posts was tested and confirmed
working as of the last release's publish date. The plugin is published in the
hope that it will be useful; in case of breakage or needed improvements, pull
requests are always welcome.
