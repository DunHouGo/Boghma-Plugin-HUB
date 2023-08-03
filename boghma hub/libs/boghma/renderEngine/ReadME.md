# renderEngine
This is a custom api for most popular render engine like Octane\Redshift\Arnold in Cinema 4D, which is also wiil contains in 'boghma' library.
```
All the boghma plugins and boghma library is FREE.
```

## Installation
To use this library, you have two options:
1. Download the source and import it to your Cinema 4D.
2. (**Not Ready Now**) You can also download [Boghma Plugin Manager](https://www.boghma.com/) and install any plugin, the boghma lib will auto installed.

# Limit
- Due to Otoy use a custom userarea for the node editor, and don't support python. We can not get the selection of the node edtor, so it is not possible to interact with node editor. 
- Redshift and Arnold material helper only support NodeGragh, so the Cinema 4D before R26 is not support.
- AddChild() and AddTextureTree() may return a not auto-layout node network now.
- GetID() is broken, wait Maxon fix it, GetParamDataTypeID() can not get vector id.
- Arnold mask tag SetPrameter has a refresh bug.


# Examples
- [__Octane Example__](./octane/octane_examples.py)
- [__Redshift Example__](./redshift/redshift_examples.py)
- [__Arnold Example__](./arnold/arnold_examples.py)


# Class Presentation

## [node_helper](./node_helper.md)
- __NodeGraghHelper__ : helper class for Cinema 4D NodeGragh.
- __TexPack__ : helper class to get texture data.
- __methods__ : helper functions.
  - get_all_nodes
  - get_nodes
  - get_tags
  - get_selection_tag
  - get_materials
  - get_texture_tag
  - select_all_materials
  - deselect_all_materials
  - get_asset_url
  - get_asset_str
  - iter_node
  - generate_random_color

## [octane_helper](./octane/Octane.md)
- __octane_id__ : unique ids for octane object, and name map of aovs.
- __octane_helper__ : all the helper class and function.
  - methods
  - VideoPostHelper (class)
  - AOVHelper (class)
  - NodeHelper (class)
  - MaterialHelper (class)
  - SceneHelper (class)

## [redshift_helper](./redshift/Redshift.md)
- __redshift__ : unique ids for redshift object, and name map of aovs.
- __redshift_helper__ : all the helper class and function.
  - methods
  - VideoPostHelper (class)
  - AOVHelper (class)
  - MaterialHelper (class)
  - RSMaterialTransaction (class)
  - SceneHelper (class)

## [arnold_helper](./arnold/Arnold.md)
- __arnold__ : unique ids for arnold object, and name map of aovs.
- __arnold_helper__ : all the helper class and function.
  - methods
  - VideoPostHelper (class)
  - AOVHelper (class)
  - MaterialHelper (class)
  - SceneHelper (class)
  - ArnoldShaderLinkCustomData (class)
  - ArnoldVColorCustomData (class)

# Version & Updates
- ### 0.1.0
  - octane_helper and node_helper is beta now. (update@2023.06.30)
- ### 0.1.1
  - redshift_helper is beta now. (update@2023.07.04)
  - add undo to octane_helper and fix some typing mistakes.
  - add **get_asset_url** and **get_asset_str** to node_helper.
  - fix some decision and add some desciption.
- ### 0.1.2
  - arnold_helper is beta now. (update@2023.07.12)
  - add **iter_node** and **generate_random_color** to node_helper.
  - **GetPort**(get outport mode) now working with arnold.
  - fix some typing mistakes.
- ### 0.1.3
  - renderEngine is beta now. (update@2023.07.16)
  - remove all the **AOVData** class and **read_aov** function(not used).
  - add **AddConnectShader** to node_helper
  - re-write redshift **MaterialHelper** with AddConnectShader.
  - re-name some redshift_helper basic functions to match arnold_helper.
- ### 1.0.0
  - renderEngine version 1.0.0 (update@2023.07.16)
- ### 1.0.1
- AovManager for arnold now have a condition. (update@2023.07.17)
- fix some typing mistakes.
- add **setup_cryptomatte** to arnold AOVHelper.
- add **CreateCryptomatte** to arnold MaterialHelper.
- ### 1.0.2
- AovManager for arnold now have a condition. (update@2023.07.25)
- fix some typing mistakes.
- add **CreateRSMaterial** to redshift MaterialHelper.
- update **CreateStandardSurface** for redshift MaterialHelper.
- ### 1.0.3
- add **set_tag_texture** to octane SceneHelper.(update@2023.07.27)
- add **set_tag_color** to octane SceneHelper.
- add **get_tag** to octane SceneHelper.
- add **get_tex_folder** to node_helper.
- add **get_texture_path** to node_helper.


---
- __coming soon...__