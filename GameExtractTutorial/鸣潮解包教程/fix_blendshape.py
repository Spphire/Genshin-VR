#blender version 3.6

import bpy
import os

# ==== 用户设定 ====

gltf_dir = r"C:\Users\Apricity\Downloads\UEViewer-master\UmodelExport\Game\Aki\Character\Role\FemaleZ\Fuludelisi\R2T1FuludelisiMd10011\Model"
scale_factor = 100.0

def select_hierarchy(obj):
    obj.select_set(True)
    for child in obj.children:
        select_hierarchy(child)

# ==================
def main():
    # 确保有选中物体
    if not bpy.context.object or bpy.context.object.type != 'MESH':
        print("请先选中一个 Mesh 对象！")
        return

    base_obj = bpy.context.object
    bpy.context.view_layer.objects.active = base_obj
    hair_groups = [vg for vg in base_obj.vertex_groups if "Hair" in vg.name]

    # 预计算所有在 Hair 组里的顶点 index
    hair_verts = set()
    for vg in hair_groups:
        for v in base_obj.data.vertices:
            try:
                if vg.weight(v.index) > 0:
                    hair_verts.add(v.index)
            except RuntimeError:
                pass  # 顶点不在此组

    # 保存原始形态键名字（跳过 Basis）
    shape_names = []
    if base_obj.data.shape_keys and base_obj.data.shape_keys.key_blocks:
        for key in base_obj.data.shape_keys.key_blocks:
            if key.name != "MORPH_BASE":
                shape_names.append(key.name)

    print("原有形态键名：", shape_names)

    # 如果没有形态键，先创建一个 Basis（保证后续 join_shapes 可用）
    if not base_obj.data.shape_keys:
        bpy.context.view_layer.objects.active = base_obj
        bpy.ops.object.shape_key_add(from_mix=False)
        base_obj.data.shape_keys.key_blocks[-1].name = "MORPH_BASE"

    # 遍历目录下的 gltf 文件（不包含 glb）
    files = [f for f in os.listdir(gltf_dir) if f.lower().endswith(".gltf")]
    files.sort()

    for f in files:
        path = os.path.join(gltf_dir, f)

        # 判断是否匹配某个形态键名
        match = None
        for name in shape_names:
            if name in f:
                match = name
                break

        if not match:
            print(f"跳过 {f} ，没有匹配到任何形态键名。")
            # 强制刷新 UI
            bpy.context.view_layer.update()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            continue

        print(f"正在导入: {path} 作为形态键 [{match}]")

        # 强制刷新 UI
        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        # 记录导入前对象集合，以便找到新导入的对象
        before_objs = set(bpy.data.objects)

        # 导入 gltf
        try:
            bpy.ops.import_scene.gltf(filepath=path)
            # 强制刷新 UI
            bpy.context.view_layer.update()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        except Exception as e:
            print(f"导入失败: {f} -> {e}")
            continue

        # 找到新导入的 mesh 对象
        new_objs = [obj for obj in bpy.data.objects if obj not in before_objs and obj.type == 'MESH']
        if not new_objs:
            print(f"文件 {f} 没有导入 mesh，跳过。")
            continue

        # 如果导入了多个 mesh，先合并为一个临时对象
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for ob in new_objs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = new_objs[0]
        if len(new_objs) > 1:
            bpy.ops.object.join()

        imported_obj = bpy.context.view_layer.objects.active

        # 缩放并应用缩放
        imported_obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.context.view_layer.objects.active = imported_obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # 将导入模型作为形态键加入或覆盖
        if match in base_obj.data.shape_keys.key_blocks:
            # 覆盖已有形态键
            shape_key = base_obj.data.shape_keys.key_blocks[match]
            for i, v in enumerate(imported_obj.data.vertices):
                # 判断该顶点是否在 Hair 组里
                if i in hair_verts:
                    # 保持 base_obj 原始顶点位置
                    shape_key.data[i].co = base_obj.data.vertices[i].co
                else:
                    # 用 imported_obj 的坐标
                    shape_key.data[i].co = v.co

            print(f"形态键 [{match}] 已覆盖（Hair 顶点保持 base_obj 原值）。")
        else:
            # 如果不存在，使用 join_shapes 新建
            bpy.ops.object.select_all(action='DESELECT')
            base_obj.select_set(True)
            imported_obj.select_set(True)
            bpy.context.view_layer.objects.active = base_obj
            try:
                bpy.ops.object.join_shapes()
                base_obj.data.shape_keys.key_blocks[-1].name = match
                print(f"形态键 [{match}] 不存在，已新建。")
            except Exception as e:
                print(f"join_shapes 失败: {e}")

        # 强制刷新 UI
        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        # 删除导入的模型及其父级层级
        root_obj = imported_obj
        while root_obj.parent:
            root_obj = root_obj.parent

        bpy.ops.object.select_all(action='DESELECT')
        select_hierarchy(root_obj)
        bpy.context.view_layer.objects.active = root_obj
        bpy.ops.object.delete()

        # 强制刷新 UI
        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    print("完成！所有匹配的 gltf 模型已覆盖/添加为形态键。")


if __name__ == '__main__':
    main()
