# Oops19 High Heels Mod - Adding CAS Sliders
## Adding the HotSpot Control

This is the generic description to add CAS controls.

Depending on the morph setting one should choose similar setting for the HotSpot controls. At least the region must match as far as I can tell.

Within TS4 Morph Maker click on:

    Create/Edit Slider and/or Preset Package
    Add/Edit Hotspot Controls (Sliders)
    [Clone HotSpotControl]
        ClonePicker Form / List of HotSpot Controls
        Sort: Region (or name, to find the slider)
        [x] Name: ... / BODY|FEET|NECK|LEG|... / Human / TYAE / Female [x] (Also the 'Male' slider may be selected here to skip this part later, often 'ym' is prepended. The select option is on the right side, not on ht left as expected)
        [x] New custom content, [Clone selected]
    Unique Name: Oops19_Slider_..._F
    Cursor Style: VerticalArrows / HorizontalArrows / ... (whatever you like)
    Age: [x] TYAE
    Frame: [-] (do not modify)
    Restrict: [-] (do not modify)
    Region: BODY|FEET|NECK|LEG|...
    Sliders > View: f, ¾r, ¾l: Modifiers: None¹ / None¹ / Oops19_..._Modifier² / None⁰  (Set everything to None to get rid of it and add modifiers where needed. In this example only on modifier is added.)
    Sliders > View: r, l [Delete] || r, l: Modifiers: None¹ / None¹ / None⁰ / None⁰ (one may keep the controls or delete them)
    Sliders > View: b [Delete] || b: Modifiers: None¹ / None¹ / None⁰ / None⁰ (one may keep the controls or delete them - depending on the cloned slider the views may be different. there may be unique views for ¾r and/od ¾l)
    [Save Slider]
    [Save HotSpotControl] (The 'Name' will change to the 'Unique Name')

    Repeat the steps above for male sims.
    Unique Name: Oops19_Slider_..._M
    Frame: [x] M
    [Save Slider]
    [Save HotSpotControl] (The 'Name' will change to the 'Unique Name')

    [Save as New Package] (Save the package as Oops19_Slider_...-CAS.package - Overwrite the previous "-CAS" version without Hotspot Controls)

## License

https://creativecommons.org/licenses/by/4.0/ | https://creativecommons.org/licenses/by/4.0/legalcode
