# Oops19 High Heels Mod - Adding CAS Sliders
## Up Down Slider

This document describes how to setup the bone sliders used for the High Heels mod.

To create the sliders 'TS MorphMaker 4.3.0.0 by CMAR' is used. To get the slider IDs S4S or S4PE has to be used, MM seems to hide this information.
Please read 'Adding_CAS_Sliders.md' first as it helps to understand this short documentation.

## Edit/Create Bone Morph
    [New File]
    Identifier: Oops19_Bonedelta_Up
    b__ROOT__: Offset:(0/1.1/0)
    [Save Bonedelta] S4_0355E0A6_00000000_92DBFA8297FB6C3D_Oops19_Bonedelta_Up.bonedelta
    Identifier: Oops19_Bonedelta_Down
    b__ROOT__: Offset:(0/-1.1/0)
    [Save Bonedelta] S4_0355E0A6_00000000_E6D6E9A4CC5A4CF6_Oops19_Bonedelta_Down.bonedelta


## Create/Edit Slider and/or Preset Package
### Add/Edit Sim Modifiers
    [Add new Sim modifier]
    Unique Morph Name: Oops19_Bonedelta_Up_Modifier
    [BoneDelta > Import] S4_0355E0A6_00000000_92DBFA8297FB6C3D_Oops19_Bonedelta_Up.bonedelta
    [x] TCTYAE
    [x] MF
    Reg: FEET
    [Save Sim Modifier] ('Sim Modifier Name' will be updated to 'Unique Morph Name')

Repeat the steps for Oops19_Bonedelta_Down with name Oops19_Bonedelta_Down_Modifier.

    [Save Sim Modifier] ('Sim Modifier Name' will be updated to 'Unique Morph Name')

    [Save as New Package] Oops19_Slider_UpDown-No_CAS.package
    [Save as New Package] Oops19_Slider_UpDown-CAS.package (Save it right now with a new name. Then add  HotSpot Controls)


### Adding the HotSpot Control

    Hotspot Control Name: FeetHotspotControl  / FEET / Human / TYAE / Female
    Unique Name: Oops19_Slider_UpDown_F
    Reg: FEET
    Sliders > View: f, ¾r, ¾l: yfheadFeel_Small / yfheadFeed_Big / Oops19_Bonedelta_Up_Modifier¹ / Oops19_Bonedelta_Down_Modifier¹        ¹NEW (Click on 'Up: [Change]' and select the modifier)

    Hotspot Control Name: ymFeetHotspotControl  / FEET / Human / TYAE / Male
    Unique Name: Oops19_Slider_UpDown_M
    Reg: FEET
    Sliders > View: f, ¾r, ¾l: ymheadFeel_Small / ymheadFeed_Big / Oops19_Bonedelta_Up_Modifier¹ / Oops19_Bonedelta_Down_Modifier¹        ¹NEW (Click on 'Up: [Change]' and select the modifier)


## In-game ID

Open 'Oops19_Slider_UpDown-No_CAS.package' with S4S and write down the ID of the 'Up' slider. In-game the 'Sim Modifier.BonePoseKey.Instance' may be used which has the same ID as select ``Type: 'Bone Pose'´´ and lookup "Key.Instance":
0xC0B2B85F24AED0E8 (with the build-in hash generator as dec: 13885363319913500904).  This ID will be used in the High Heels configuration file.
The ID of the 'Down' slider is 0x90230AAF840A6C72. It is currently not used.

'Oops19_Slider_UpDown-CAS.package' has the same ID but as it contains more files it's harder to locate.
Use either Oops19_Slider_Height.package or Oops19_Slider_Height_No-CAS-Controls.package. Using both files may lead to unexpected results.


## WARNING

If this ID changes after a re-creation be sure to replace the slider IDs in the preset files accordingly.
If the one of the bone delta morph values offset, scale or rot are modified the slider values in the configuration files have to be adjusted accordingly.

Please create your own No-CAS sliders and bundle them with your content if needed. Or better let me know whether and how I can bundle better sliders.
If you contribute please use the https://creativecommons.org/licenses/by/4.0/ license to make sure the sliders can be used even commercially.


## License

https://creativecommons.org/licenses/by/4.0/ | https://creativecommons.org/licenses/by/4.0/legalcode
