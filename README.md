# pycraft2

![alt text][bot_vs_bot_gif]

[bot_vs_bot_gif]: https://github.com/jrtknauer/pycraft2/raw/main/.github/assets/pycraft2.gif "pycraft2 bot versus bot gif"

**pycraft2** is a Python package for implementing scripted bots for the real-time strategy game *StarCraft II*.

- [About pycraft2](#about-pycraft2)
    - [Development Status](#development-status)
    - [Roadmap](#roadmap)
    - [Motivation](#motivation)

# About pycraft2

## Development Status

**pycraft2** currently implements the [s2client-proto](https://github.com/Blizzard/s2client-proto) state machine for:

- Local Bot vs Built-in AI.
- Local Bot vs Bot.
- Joining [AI Arena](https://aiarena.net) ladder matches - *with caveats discussed below*.

*What's missing?*

While **pycraft2** can launch a match and play it to completion, bots cannot currently be scripted to do anything as
the raw data interfaces are still in development.

There is also the dependency issue when it comes to the AI Arena ladder. AI Arena currently uses
[sc2-ai-match-controller](https://github.com/aiarena/sc2-ai-match-controller) to facilitate matches between bots on
the ladder. Each bot runs in a container created from
[aiarenaclient-bot-base](https://hub.docker.com/r/aiarena/arenaclient-bot-base/), which installs all of the
dependencies from the major *StarCraft II* scripted bot frameworks - including **python-sc2**. Therefore, using **pycraft2**
for ladder bot development must be done in conjunction with a bundler (e.g.
[Pyinstaller](https://pyinstaller.org/en/stable/)) to avoid conflicting dependencies.

## Roadmap

**pycraft2** is in the early stages of development. However, there is a definitive set of features which will be
support as part of the 1.0 release:

- A unified interface for running local matches, specifically:
    - Bot vs Built-in AI
    - Bot vs Bot
- An interface to support play on the [AI Arena](https://aiarena.net/) ladder.
    - AI Arena is the defacto ladder for scripted bots, so **pycraft2** will provide first-class support for its
    interfaces.
- A complete implementation of the [s2client-proto raw data interface](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#raw-data).
- A complete implementation of the [s2client-proto debug interface](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/debug.proto)
  to enable a comprehensive test suite for **pycraft2**.

What **pycraft2** **will not implement** are any "helper" abstractions for facilitating the development of scripted bot
logic (e.g. a re-usable function for finding the nearest base expansion). **pycraft2**'s design goal is to provide clear
library interfaces to create, test, and launch scripted *StarCraft II* bots; this is a library, **not a framework**.
The [feature layer interface](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#feature-layer)and
[rendered interface](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#rendered) will also not
be implemented.

## Motivation

> Why release **pycraft2** when the **python-sc2** library and **sharpy-sc2** framework already exist?

Three reasons:

- Personal interest
- Implementing what I believe to be a more concise and stable interface for **s2client-proto**.
- Investigating documentation holes in **s2client-proto** and related issues for scripted bot development.

If you are looking to start building scripted bots in Python today, then [python-sc2](https://github.com/BurnySc2/python-sc2)
and [sharpy-sc2](https://github.com/DrInfy/sharpy-sc2) are both excellent resources to use. My own requirements have
outgrown the architectural foundations of **python-sc2**, so I have committed to a ground-up rewrite.

For my personal interests, this is also an opportunity to experiment with various software designs, test new development
tools, and document my findings to contribute to the [StarCraft II AI community discord](https://discordapp.com/invite/zXHU4wM)
and [AI Arena](https://aiarena.net/wiki/bot-development/) bot development resources.

> Why is **s2client-proto** a git submodule. Why are the compiled protocol buffer Python API source files embedded within
> **pycraft2**? Why not just use [s2clientprotocol](https://pypi.org/project/s2clientprotocol/)?

I am opting to not use the **s2clientprotocol** package published by Blizzard, and instead generate and integrate the
Python API directly into **pycraft2** because `s2clientprotocol` is packaged without type stubs. While I have opened a
[pull request for s2client-proto](https://github.com/Blizzard/s2client-proto/pull/204) to have the type stubs
distributed with the official package, I do not expect the pull request to be accepted as the repository is in
maintenance mode and has not accepted a pull request in over a year (and I have no desire to maintain a fork).

As a contingency I have also opened a separate [pull request for typeshed](https://github.com/python/typeshed/pull/10372),
but I also do not expect this pull request to be merged as the [mypy-protobuf](https://github.com/nipunn1313/mypy-protobuf)
generated type-stubs fail for some of **typeshed**'s third-party tests.

My solution is to integrate the generated Python API within **pycraft2** with with the type stubs - similar to how
[cpp-sc2 fetches and compiles](https://github.com/cpp-sc2/cpp-sc2/blob/master/thirdparty/cmake/sc2protocol.cmake)
the protocol buffers from source.
