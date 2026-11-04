
# ShopEngine

**Minecraft Shop Configuration Plugin Converter**

_Version 1 · AI-Assisted Prototype_

ShopEngine is a GUI-based utility designed to convert Minecraft shop configurations between different plugin formats.

It aims to make transferring and managing shop data easier for Minecraft server administrators and plugin developers.

> [!WARNING]
> **V1 — Best-Effort Support Only**
>
> V1 was developed with AI assistance. It is provided as-is, without guaranteed bug fixes, maintenance, or future updates. Unexpected errors and inconsistent behavior may occur.

---

## ⚠️ Important Notice

- This program requires a valid `.yml` or `.yaml` shop configuration file.
- Make sure you have obtained the configuration file legally.
- Always back up your original configuration before conversion.
- Conversion results may contain errors or unexpected changes.
- The developer is not responsible for copyright violations involving files supplied by users.
- This software is provided as-is.

## Overview

ShopEngine allows you to convert Minecraft shop configurations between different plugin formats through a graphical user interface.

It is designed purely as a utility to make managing shop data easier for server administrators and plugin developers.

**Development note:** V1 was developed with AI assistance. The original implementation was not entirely written by the developer. V2 is intended to be a more independently developed implementation.

## Requirements

- Python 3.8 or newer
- PyYAML

The application uses Python's built-in libraries for its GUI and other functionality. PyYAML is the only external Python dependency.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/RimakiTaema/Shopengine.git
```

### 2. Navigate into the project directory

```bash
cd Shopengine
```

### 3. Install PyYAML

```bash
python3 -m pip install PyYAML
```

### 4. Run ShopEngine

```bash
python3 shop-converter.py
```

## Usage

ShopEngine uses a graphical user interface (GUI), so the conversion process is straightforward.

1. Launch ShopEngine.
2. Select your source shop configuration file.
3. Choose the appropriate conversion format.
4. Start the conversion process.
5. Review the generated configuration.
6. Test the converted configuration before deploying it to your production server.

*Available conversion formats depend on the implementation.*

## Compatibility

ShopEngine is designed for Minecraft shop configuration files using YAML.

Compatibility depends on the source and destination plugin formats.

Different plugins may use different:
- YAML structures
- Item definitions
- Pricing systems
- Configuration conventions
- Custom metadata

Not every configuration or plugin version is guaranteed to work.

## Version Support Policy

| Support Category | V1 |
|---|---|
| Availability | Available |
| Bug fixes | Not guaranteed |
| Future updates | Not guaranteed |
| Technical support | Best effort |
| Compatibility guarantees | None |
| Maintenance | Not guaranteed |

### Why does V1 have limited support?

V1 was developed using AI-assisted coding. Because of the nature of its original implementation, errors may be difficult to reproduce, diagnose, or resolve.

Issues may be reported, but there is no guarantee that they will be investigated or fixed.

The developer reserves the right to discontinue V1 maintenance at any time.

## Disclaimer

ShopEngine is an independent community utility.

It is not affiliated with, endorsed by, or officially associated with Minecraft, Mojang Studios, Microsoft, or any supported Minecraft plugin developers.

Users are responsible for:
- Ensuring they have permission to use their configuration files.
- Maintaining backups of original configurations.
- Checking conversion results.
- Testing converted configurations before production use.

The software is provided "AS IS", without warranties of any kind.

## Development

**Developer:** RimakiTaema

**Repository:** https://github.com/RimakiTaema/Shopengine/

**Version:** V1

**Development Type:** AI-assisted

**Support Status:** Best-effort / No guaranteed maintenance

---

*ShopEngine V1 — A simple utility for Minecraft shop configuration conversion.*
