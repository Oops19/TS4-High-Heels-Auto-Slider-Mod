# Oops19 High Heels Mod - Adding CAS Sliders
## Tall Little Slider

This document describes how to setup the bone sliders used for the High Heels mod.

To create the sliders 'TS MorphMaker 4.3.0.0' is used. To get the slider IDs S4S or S4PE has to be used, MM seems to hide this information.
Please read 'Adding_CAS_Sliders.md' first as it helps to understand this short documentation.

This slider is not meant to be used with min values as the used feet IK bones seem to be unaffected by scaling.

## Edit/Create Bone Morph

    [New File]
    Identifier: Oops19_Bonedelta_Tall
    b__ROOT__: Scale:(0.58/0.58/0.58) # y*0.58 ~ +1m  (X, Y and Z have to be set to the same value. Otherwise the sim will fly in-game instead of changing the height.)
    [Save Bonedelta] S4_0355E0A6_00000000_F41060A51D176ADB_Oops19_Bonedelta_Tall.bonedelta
    Identifier: Oops19_Bonedelta_Little
    b__ROOT__: Scale:(-0.58/-0.58/-0.58) # y*0.58 ~ -1m  (X, Y and Z have to be set to the same value. Otherwise the sim will fly in-game instead of changing the height.)
    [Save Bonedelta] S4_0355E0A6_00000000_E6D6E9A4CC5A4CF6_Oops19_Bonedelta_Little.bonedelta


## Create/Edit Slider and/or Preset Package
### Add/Edit Sim Modifiers

    [Add new Sim modifier]
    Unique Morph Name: Oops19_Bonedelta_Tall_Modifier
    [BoneDelta > Import] S4_0355E0A6_00000000_F41060A51D176ADB_Oops19_Bonedelta_Tall.bonedelta
    [x] TCTYAE
    [x] MF
    Reg: NECK
    [Save Sim Modifier] ('Sim Modifier Name' will be updated to 'Unique Morph Name')

Repeat the steps for Oops19_Bonedelta_Little with name Oops19_Bonedelta_Little_Modifier.

    [Save Sim Modifier] ('Sim Modifier Name' will be updated to 'Unique Morph Name')

    [Save as New Package] Oops19_Slider_TallLittle-No_CAS.package
    [Save as New Package] Oops19_Slider_TallLittle-CAS.package (Save it right now with a new name. Then add  HotSpot Controls)



## In-game ID

Open 'Oops19_Slider_TallLittle-No_CAS.package' with S4S and write down the ID of the 'Tall' slider. In-game the 'Sim Modifier.BonePoseKey.Instance' may be used which has the same ID as select ``Type: 'Bone Pose'´´ and lookup "Key.Instance":
0xFF37A81444FDFC7D (with the build-in hash generator as dec: 18390352408401017981). This ID will be used in the High Heels configuration file.
The ID of the 'Little' slider is 0xB36AA2707A598EAC. It is currently not used.

'Oops19_Slider_TallLittle-CAS.package' has the same ID but as it contains more files it's harder to locate.
Use either Oops19_Slider_Height.package or Oops19_Slider_Height_No-CAS-Controls.package. Using both files may lead to unexpected results.


## WARNING

If this ID changes after a re-creation be sure to replace the slider IDs in the preset files accordingly.
If the one of the bone delta morph values offset, scale or rot are modified the slider values in the configuration files have to be adjusted accordingly.

Please create your own No-CAS sliders and bundle them with your content if needed. Or better let me know whether and how I can bundle better sliders.
If you contribute please use the https://creativecommons.org/licenses/by/4.0/ license to make sure the sliders can be used even commercially.


## License

https://creativecommons.org/licenses/by/4.0/ | https://creativecommons.org/licenses/by/4.0/legalcode
