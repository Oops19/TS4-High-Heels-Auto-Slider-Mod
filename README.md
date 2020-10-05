# Oops19 High Heels Mod
## Introduction

This mod allows to modify sliders based on the outfit. When a sim wears heels or boots the standard TS4 implementation reduces the length of the calf bone accordingly.
This mod applies a scale slider to compensate this. The sim will be taller (or if desired for magic boots smaller) in-game.

Also 'up/down' sliders are supported. The well-known 'SLIDER' boots usually use an 'up' or 'fly' slider. This works much better than scaling the sim.

## Warning

This is a beta mod which adds sliders to your sim. Please make a backup of your save game and keep it for reference if you want to use this mod.
It takes about 0.5 seconds to set the sliders and the game may delay the adjustment of the settings even further.

Tested with 'The Sims 4' v1.65.77.1020 (8/18/2020) and S4CL v1.30. As soon as I'm ready to break my window CC it will be tested with the newest version. Though it may work without any issues.

## Installation
It is recommended to read the whole README but to get started download the ZIP file and extract it to the 'The Sims 4' directory. Or better to a temporary directory to make sure to copy over only the two sliders and the '\_Oops19-Debug\_' directory which must be placed in Mods (not in a sub folder).

Install [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases) as this mod is required.

## Supported shoes

### Base game * EP * SP * AP
Currently many (all except Toddler Stuff, Nifty Knitting, Eco Lifestlye, Journey to Batuu) base game female shoes are supported.

### Dallasgirl79
Older shoes of [Dallasgirl79](https://dallasgirl79.tumblr.com/) are supported, but only the SLIDER version. The normal version is not supported.

The [Pia Heels](https://www.patreon.com/posts/39052976) heels are an exception as they do not support sliders. The setup is complicated with feet (CAS category: Shoes), random toe nail colors (CAS category: socks) and heels (CAS category: tights).

### Astya96
The Valentine slider Heels  of Astya96 https://www.patreon.com/posts/33961061 are supported.

### ATS4
The hoverboard https://sims4.aroundthesims3.com/objects/special_06.shtml is not yet supported. In the near future while wearing an item (shoe) also a build item (hoverboard) can be attached to a random sim bone.

## Supported walk style
The walk style may be set based on the selected shoes or any other used CAS item.
The default is 'Walk Feminine Slow'.

## Usage

The mod does not include a PIE menu. It detects cloth changes and applies slider afterwards, based on the outfit.
It does not support all available shoes. Only shoes which are configured (see above) are supported.

## Customization

There is no option to gather slider values from a .package file. All configurations for CAS items is stored externally in the 'configuration' directory.

New sliders are configured there. Use 'TS MorphMaker 4.3.0.0 by CMAR' or something else to create new sliders is needed or use existing sliders.
Also the presets are stored there.

The _slider.sample.ini and _preset.sample.ini files contain more documentation.

Longer arms while wearing gloves, slim- or shapewear may also be configured. Also getting a long nose when wearing a special ring should work.
Both body and face sliders may be modified. Face presets can not be modified.

## Developers and Modders

Any help is welcome. I'm still looking for sliders to stretch the calf bone to use them instead of changing the scale of the sim.

The code is open source and is lice Attribution-NonCommercial-NoDerivatives license.

This development version includes a lot of code to extract slider, walk style, CAS IDs and other game data which may be useful for other projects. The license for this mod is 'Attribution-NonCommercial-NoDerivatives' (to be changed to 'Attribution' in 2021) while the additional test tools are already licensed with an 'Attribution' license.
