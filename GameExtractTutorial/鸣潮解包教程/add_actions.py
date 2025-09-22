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

for action in bpy.data.actions:
    if action.name.endswith("_Combined"):
        avatar.animation_data.action = action
        pushdown_action(avatar, blend_type='REPLACE')
