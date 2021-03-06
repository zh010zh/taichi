import taichi as ti

# A set of helper (meta)functions


@ti.kernel
def fill_tensor(tensor: ti.template(), val: ti.template()):
    for I in ti.grouped(tensor):
        tensor[I] = val


@ti.kernel
def tensor_to_ext_arr(tensor: ti.template(), arr: ti.ext_arr()):
    for I in ti.grouped(tensor):
        arr[I] = tensor[I]


@ti.func
def cook_image_type(x):
    x = ti.cast(x, ti.f32)
    return x


@ti.kernel
def vector_to_fast_image(img: ti.template(), out: ti.ext_arr()):
    # FIXME: Why is ``for i, j in img:`` slower than:
    for i, j in ti.ndrange(*img.shape):
        u, v, w = min(255, max(0, int(img[i, img.shape[1] - 1 - j] * 255)))
        # We use i32 for |out| since OpenGL and Metal doesn't support u8 types
        # TODO: treat Cocoa and Big-endian machines, with XOR logic
        out[j * img.shape[0] + i] = w + (v << 8) + (u << 16)


@ti.kernel
def tensor_to_image(tensor: ti.template(), arr: ti.ext_arr()):
    for I in ti.grouped(tensor):
        t = cook_image_type(tensor[I])
        arr[I, 0] = t
        arr[I, 1] = t
        arr[I, 2] = t


@ti.kernel
def vector_to_image(mat: ti.template(), arr: ti.ext_arr()):
    for I in ti.grouped(mat):
        for p in ti.static(range(mat.n)):
            arr[I, p] = cook_image_type(mat[I][p])
            if ti.static(mat.n <= 2):
                arr[I, 2] = 0


@ti.kernel
def tensor_to_tensor(tensor: ti.template(), other: ti.template()):
    for I in ti.grouped(tensor):
        tensor[I] = other[I]


@ti.kernel
def ext_arr_to_tensor(arr: ti.ext_arr(), tensor: ti.template()):
    for I in ti.grouped(tensor):
        tensor[I] = arr[I]


@ti.kernel
def matrix_to_ext_arr(mat: ti.template(), arr: ti.ext_arr(),
                      as_vector: ti.template()):
    for I in ti.grouped(mat):
        for p in ti.static(range(mat.n)):
            for q in ti.static(range(mat.m)):
                if ti.static(as_vector):
                    arr[I, p] = mat[I][p]
                else:
                    arr[I, p, q] = mat[I][p, q]


@ti.kernel
def ext_arr_to_matrix(arr: ti.ext_arr(), mat: ti.template(),
                      as_vector: ti.template()):
    for I in ti.grouped(mat):
        for p in ti.static(range(mat.n)):
            for q in ti.static(range(mat.m)):
                if ti.static(as_vector):
                    mat[I][p] = arr[I, p]
                else:
                    mat[I][p, q] = arr[I, p, q]


@ti.kernel
def clear_gradients(vars: ti.template()):
    for I in ti.grouped(ti.Expr(vars[0])):
        for s in ti.static(vars):
            ti.Expr(s)[I] = 0


@ti.kernel
def clear_loss(l: ti.template()):
    # Using SNode writers would result in a forced sync, therefore we wrap these
    # writes into a kernel.
    l[None] = 0
    l.grad[None] = 1


@ti.kernel
def fill_matrix(mat: ti.template(), vals: ti.template()):
    for I in ti.grouped(mat):
        for p in ti.static(range(mat.n)):
            for q in ti.static(range(mat.m)):
                mat[I][p, q] = vals[p][q]


@ti.kernel
def snode_deactivate(b: ti.template()):
    for I in ti.grouped(b):
        ti.deactivate(b, I)


@ti.kernel
def snode_deactivate_dynamic(b: ti.template()):
    for I in ti.grouped(b.parent()):
        ti.deactivate(b, I)
