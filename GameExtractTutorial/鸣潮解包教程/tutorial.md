## umodel 解包blendshape
umodel 本体源码[下载](
https://github.com/gildor2/UEViewer/releases)

umodel acl组件[下载](
https://www.gildor.org/smf/index.php/topic,8304.msg42970.html#msg42970)

将acl组件放在源码根目录下运行

路径选到client/content/paks

override引擎选4，右侧游戏选鸣潮

### AES

0x6F80948821CA338739A24D4D9F778BCAC0996B2EF2A73897A789C68AFF05174E
0x775BB51049A593ABE631F96253719F3F2E136BBC123E93D4F2A735202111B48E
0x30418E1E966518A937CF25285B88B90830BFEC7B06FE975B6ED99E1AD92E55F7
0x5E45B92BF5048D2A2FDA6D42A263F6FDC4A3A4915A53E1BB42CEBCCA677D6059
0xDD84820F5D3AE9B354BFDA146930FD77873A367AA77DDD0F304667DA5EFD171D

glTF导出模型 勾选export morphed models
会有一堆gltf文件

统统导入blender

{在本体的mesh节点（三角形符号）上data属性（倒三角符号）添加一个base形态键（+按钮）

主窗口按a全选，选中本体的mesh，形态键UI右侧（下箭头）join as shapes}

s放大100倍，ctrl+a应用，将gltf合并至psk模型，这样还能接收psa动画

导入unity的fbx需要将blendshape normal从compute改为import


## fmodel 解包animation

fmodel解包psk模型以及psa动画[AES](https://github.com/ClostroOffi/wuwa-aes-archive)

版本号aa75a8b 

鸣潮版本2.6

[参考视频](https://www.bilibili.com/video/BV14AhRzZExb/?spm_id_from=333.1387.upload.video_card.click&vd_source=6d24f292fae98583d376dd53fd47af3b)

## 脚本解释

fix_blendshape.py

批量合并每个blendshape模型

bake_pas.py

批量烘焙角色动画与物理动画

[参考视频](https://www.bilibili.com/video/BV1nWVBztEKH/?spm_id_from=333.337.search-card.all.click&vd_source=6d24f292fae98583d376dd53fd47af3b)

add_actions.py

添加烘焙好的动画