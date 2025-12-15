import bpy
import numpy as np

def get_k_nearest_weights(target_co, vertices_co, k=5):
    """
    Finds k-nearest vertices and calculates weights using Inverse Distance Weighting (IDW).
    """
    # Calculate distances to all vertices
    dists = np.linalg.norm(vertices_co - target_co, axis=1)
    
    # Get indices of k closest vertices
    # np.argpartition is faster than sort for finding k smallest
    if len(dists) <= k:
        k_indices = np.arange(len(dists))
    else:
        k_indices = np.argpartition(dists, k)[:k]
        
    k_dists = dists[k_indices]
    
    # Avoid division by zero (if distance is very small, give full weight to that vertex)
    epsilon = 1e-6
    if np.any(k_dists < epsilon):
        weights = np.zeros(len(k_dists))
        weights[np.argmin(k_dists)] = 1.0
        return k_indices, weights
        
    # Inverse Distance Weighting (IDW)
    # Using squared distance gives sharper falloff (w = 1/d^2)
    inv_dists = 1.0 / (k_dists ** 2)
    weights = inv_dists / np.sum(inv_dists)
    
    return k_indices, weights

def constraint_bone_to_vertex():
    # 1. Validation: Check selections
    selected_objects = bpy.context.selected_objects
    if len(selected_objects) != 2:
        print("Error: Please select exactly two objects (One Mesh, One Armature).")
        return

    mesh_obj = None
    armature_obj = None

    for obj in selected_objects:
        if obj.type == 'MESH':
            mesh_obj = obj
        elif obj.type == 'ARMATURE':
            armature_obj = obj

    if not mesh_obj or not armature_obj:
        print("Error: Selection must include one Mesh and one Armature.")
        return

    # 2. Data Preparation
    # Ensure we are in Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bone_names = [bone.name for bone in armature_obj.data.bones]
    vertices = np.array([v.co for v in mesh_obj.data.vertices]) # Optimization: cache coordinates directly
    
    # 3. Process Each Bone
    for bone_name in bone_names:
        pose_bone = armature_obj.pose.bones[bone_name]
        data_bone = armature_obj.data.bones[bone_name]
        
        # --- Common Logic: Tail to Nearest Vertex (for IK) ---
        bone_tail_world = armature_obj.matrix_world @ pose_bone.tail
        # For vertex distance calculation, we need vertex coords in World Space or both in Local.
        # It's usually easier to bring bone coords to Mesh Local Space or Mesh Verts to World.
        # Let's bring Bone Point to Mesh Local Space for comparison with v.co
        bone_tail_mesh_local = mesh_obj.matrix_world.inverted() @ bone_tail_world
        
        # Find k closest vertices and weights
        indices, weights = get_k_nearest_weights(bone_tail_mesh_local, vertices, k=5)
        
        # Create Vertex Group for IK
        if bone_name not in mesh_obj.vertex_groups:
            vg = mesh_obj.vertex_groups.new(name=bone_name)
        else:
            vg = mesh_obj.vertex_groups[bone_name]
            
        # Add weights to vertex group
        for idx, weight in zip(indices, weights):
            vg.add([int(idx)], weight, 'REPLACE')
        
        # --- Root Bone Logic: Head to Nearest Vertex (for Copy Location) ---
        if data_bone.parent is None:
            # This is a root bone
            root_vg_name = f"{bone_name}_root"
            
            bone_head_world = armature_obj.matrix_world @ pose_bone.head
            bone_head_mesh_local = mesh_obj.matrix_world.inverted() @ bone_head_world
            
            # Find closest vertex index to head (Weighted)
            indices_head, weights_head = get_k_nearest_weights(bone_head_mesh_local, vertices, k=5)
            
            # Create Vertex Group for Root Anchor
            if root_vg_name not in mesh_obj.vertex_groups:
                root_vg = mesh_obj.vertex_groups.new(name=root_vg_name)
            else:
                root_vg = mesh_obj.vertex_groups[root_vg_name]
                
            # Add weights to vertex group
            for idx, weight in zip(indices_head, weights_head):
                root_vg.add([int(idx)], weight, 'REPLACE')
            
            # Add Copy Location Constraint FIRST
            # Remove existing Copy Location if any (for idempotency)
            copy_loc = pose_bone.constraints.get("Copy Location")
            if not copy_loc:
                copy_loc = pose_bone.constraints.new(type='COPY_LOCATION')
            
            # Move constraint to top of stack if needed, though 'new' usually adds to end.
            # Ideally Copy Location handles position, IK handles rotation/stretch towards tail.
            
            copy_loc.target = mesh_obj
            copy_loc.subtarget = root_vg_name
            # Copy Location usually works best for roots to pin them.
        
        # --- Add IK Constraint ---
        ik_constraint = pose_bone.constraints.get("IK")
        if not ik_constraint:
            ik_constraint = pose_bone.constraints.new(type='IK')
            
        ik_constraint.target = mesh_obj
        ik_constraint.subtarget = bone_name
        ik_constraint.chain_count = 1

    print("Successfully created weighted vertex groups and constraints.")

# Execute the function
constraint_bone_to_vertex()
