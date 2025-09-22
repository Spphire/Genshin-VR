#blender version 4.5 (import function supported by psk plugin)

# character_psa_folder = r"C:\Users\Apricity\Desktop\2025-2\FModel\output\Exports\Client\Content\Aki\Character\Role\FemaleZ\Fuludelisi\CommonAnim"
# physics_psa_folder   = r"C:\Users\Apricity\Desktop\2025-2\FModel\output\Exports\Client\Content\Aki\Character\Role\FemaleZ\Fuludelisi\R2T1FuludelisiMd10011\RibbonAnim"

# character_psa_folder = r"C:\Users\Apricity\Desktop\2025-2\WutheringWaves\bake_pas\common"
# physics_psa_folder = r"C:\Users\Apricity\Desktop\2025-2\WutheringWaves\bake_pas\ribbon"

import bpy
import os


def pushdown_action(obj, blend_type='REPLACE'):
    """
    模拟 bpy.ops.nla.action_pushdown()
    将 obj.animation_data.action 存入新的 NLA Track，并设置 Strip 的 blend_type
    """
    ad = obj.animation_data
    if ad is None or ad.action is None:
        return None

    # 创建 NLA Track
    track = ad.nla_tracks.new()
    track.name = ad.action.name + "_Track"

    # 创建 Strip
    strip = track.strips.new(ad.action.name, int(ad.action.frame_range[0]), ad.action)

    # 设置 Strip 的混合模式
    strip.blend_type = blend_type

    # 清空当前动作
    ad.action = None

    return track, strip


# ==== 用户设定 ====
avatar = bpy.context.object
if not avatar:
    raise Exception("请先选择一个 avatar 对象！")

character_psa_folder = r"C:\Users\Apricity\Desktop\2025-2\FModel\output\Exports\Client\Content\Aki\Character\Role\FemaleZ\Fuludelisi\CommonAnim"
physics_psa_folder   = r"C:\Users\Apricity\Desktop\2025-2\FModel\output\Exports\Client\Content\Aki\Character\Role\FemaleZ\Fuludelisi\R2T1FuludelisiMd10011\RibbonAnim"

# ==== 获取文件列表并建立字典 ====
character_files = [f for f in os.listdir(character_psa_folder) if f.lower().endswith(".psa")]
physics_files = [f for f in os.listdir(physics_psa_folder) if f.lower().endswith(".psa")]
physics_dict = {f[4:]: f for f in physics_files if f.startswith("Rib_")}

# ==== 主循环 ====
for char_file in character_files:
    phys_file = physics_dict.get(char_file)
    if not phys_file:
        print(f"跳过 {char_file}，未找到对应物理动画")
        continue  # 没有对应物理动画则跳过

    char_path = os.path.join(character_psa_folder, char_file)
    phys_path = os.path.join(physics_psa_folder, phys_file)
    print(f"处理动画对: {char_file} + {phys_file}")

    # 用文件名生成 base_name
    base_name = os.path.splitext(char_file)[0]

    # ==== 确保 avatar 有 animation_data ====
    if avatar.animation_data is None:
        avatar.animation_data_create()

    # ==== 导入物理动画 ====
    bpy.ops.psa.import_all(filepath=phys_path)
    phys_action = bpy.data.actions.get("Rib_" + base_name)
    avatar.animation_data.action = phys_action

    # 删除 Root 骨骼关键帧
    if "Root" in avatar.pose.bones:
        root_fcurves = [fc for fc in phys_action.fcurves if fc.data_path.startswith('pose.bones["Root"]')]
        for fc in root_fcurves:
            phys_action.fcurves.remove(fc)
        print("已删除 Root 骨骼关键帧")

    pushdown_action(avatar, "REPLACE")

    # 强制刷新 UI
    bpy.context.view_layer.update()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    print(f"物理动画 {phys_file} 导入成功！")

    # ==== 导入角色动画 ====
    bpy.ops.psa.import_all(filepath=char_path)
    char_action = bpy.data.actions.get(base_name)
    avatar.animation_data.action = char_action

    # 强制刷新 UI
    bpy.context.view_layer.update()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    print(f"角色动画 {char_file} 导入成功！")

    pushdown_action(avatar, "COMBINE")

    # 强制刷新 UI
    bpy.context.view_layer.update()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    # ==== 烘焙合并动画 ====
    frame_start = int(char_action.frame_range[0])
    frame_end = int(char_action.frame_range[1])

    combined_action = bpy.data.actions.new(name=base_name + "_Combined")
    avatar.animation_data.action = combined_action

    bpy.ops.nla.bake(frame_start=frame_start,
                     frame_end=frame_end,
                     only_selected=False,
                     visual_keying=True,
                     clear_constraints=True,
                     use_current_action=True,
                     bake_types={'POSE'})

    print(f"已生成烘焙合并动画: {combined_action.name}")

    # ==== 删除临时数据 ====
    for track in list(avatar.animation_data.nla_tracks):
        for strip in list(track.strips):
            track.strips.remove(strip)
        avatar.animation_data.nla_tracks.remove(track)
    avatar.animation_data.action = None
    for action in list(bpy.data.actions):  # 用 list() 避免迭代时修改集合
        if action.name.split('.')[0].endswith(base_name):  # 这里用 base_name 过滤
            bpy.data.actions.remove(action)

    # 强制刷新 UI
    bpy.context.view_layer.update()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

print("所有动画处理完成！")
