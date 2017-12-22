#Copyright (c) 2017 William Emerison Six
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import sys
import os
import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders
import numpy as np
import glfw.glfw as glfw
import pyMatrixStack as ms
import ctypes
import math
import nuklear as nk

if __name__ != '__main__':
    sys.exit(1)

pwd = os.path.dirname(os.path.abspath(__file__))

glfloat_size = 4

floatsPerVertex = 3

class Triangle:
    def __init__(self):
        pass

    def prepareToRender(self):
        vertices = np.array([-0.6,  -0.4,  0.0,
                             0.6,   -0.4,  0.0,
                             0,     0.6,   0.0],
                            dtype=np.float32)

        self.numberOfVertices = np.size(vertices) // floatsPerVertex


        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        #initialize shaders

        with open(os.path.join(pwd, '..', 'shaders', 'triangle.vert'), 'r') as f:
            vs = shaders.compileShader(f.read() , gl.GL_VERTEX_SHADER)

        with open(os.path.join(pwd, '..', 'shaders', 'triangle.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), gl.GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs,fs)

        self.mvpMatrixLoc = gl.glGetUniformLocation(self.shader,"mvpMatrix")

        #send the modelspace data to the GPU
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        position = gl.glGetAttribLocation(self.shader, 'position')
        gl.glEnableVertexAttribArray(position)

        gl.glVertexAttribPointer(position,
                                 floatsPerVertex,
                                 gl.GL_FLOAT,
                                 False,
                                 0,
                                 ctypes.c_void_p(0))

        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        glfloat_size * np.size(vertices),
                        vertices,
                        gl.GL_STATIC_DRAW)

        # reset VAO/VBO to default
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER,0)


    def render(self):
        with ms.GLStackProtector(ms.MatrixStack.model):
            # rotate the triangle along the positive z axis
            ms.translate(ms.MatrixStack.model,
                         math.sin(glfw.glfwGetTime()),
                         0,
                         0)
            ms.rotateZ(ms.MatrixStack.model,glfw.glfwGetTime())

            gl.glUseProgram(self.shader)
            gl.glBindVertexArray(self.vao)


            gl.glUniformMatrix4fv(self.mvpMatrixLoc,
                                  1,
                                  gl.GL_TRUE,
                                  np.ascontiguousarray(
                                      ms.getCurrentMatrix(ms.MatrixStack.modelviewprojection),
                                      dtype=np.float32))
            gl.glDrawArrays(gl.GL_TRIANGLES,
                            0,
                            self.numberOfVertices)
            gl.glBindVertexArray(0)



# Initialize the library
if not glfw.glfwInit():
    sys.exit()

glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR,3)
glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR,3)
glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE,glfw.GLFW_OPENGL_CORE_PROFILE)
#for osx
glfw.glfwWindowHint(glfw.GLFW_OPENGL_FORWARD_COMPAT, gl.GL_TRUE)


# Create a windowed mode window and its OpenGL context
window = glfw.glfwCreateWindow(1000, 1000, str.encode("Hello World"), None, None)
if not window:
    glfw.glfwTerminate()
    sys.exit()

# Make the window's context current
glfw.glfwMakeContextCurrent(window)

ctx = nk.glfw3_init(window, nk.GLFW3_INSTALL_CALLBACKS)
nuklear = nk.NuklearContext(ctx)

fontAtlas = nk.FontAtlas()
nk.glfw3_font_stash_begin(ctypes.byref(fontAtlas))
nk.glfw3_font_stash_end()

# Install a key handler
def on_key(window, key, scancode, action, mods):
    if key == glfw.GLFW_KEY_ESCAPE and action == glfw.GLFW_PRESS:
        glfw.glfwSetWindowShouldClose(window,1)
glfw.glfwSetKeyCallback(window, on_key)

gl.glClearColor(0.0,0.0,0.0,1.0)
gl.glEnable(gl.GL_DEPTH_TEST)
gl.glClearDepth(1.0)
gl.glDepthFunc(gl.GL_LEQUAL)



class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 10.0

        self.rotationX = 0.0
        self.rotationY = 0.0

camera = Camera()

triangle = Triangle()
triangle.prepareToRender()

# does python have static local variables?  this declaration is way too far away from use
#property = ctypes.c_int(20)


# Loop until the user closes the window
while not glfw.glfwWindowShouldClose(window):
    # Render here

    # Poll for and process events
    glfw.glfwPollEvents()
    nk.glfw3_new_frame()

    width, height = glfw.glfwGetFramebufferSize(window)
    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    ms.setToIdentityMatrix(ms.MatrixStack.model)
    ms.setToIdentityMatrix(ms.MatrixStack.view)
    ms.setToIdentityMatrix(ms.MatrixStack.projection)

    # set the projection matrix to be perspective
    ms.perspective(fov= 45.0,
                   aspectRatio= width / height,
                   nearZ= 0.1,
                   farZ= 10000.0)

    # get input from keyboard for camera movement
    if not nuklear.item_is_any_active():
        # set up Camera
        if glfw.glfwGetKey(window, glfw.GLFW_KEY_RIGHT) == glfw.GLFW_PRESS:
            camera.rotationY -= 0.03

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_LEFT) == glfw.GLFW_PRESS:
            camera.rotationY += 0.03

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_UP) == glfw.GLFW_PRESS:
            camera.x -= math.sin(camera.rotationY)
            camera.z -= math.cos(camera.rotationY)

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_DOWN) == glfw.GLFW_PRESS:
            camera.x += math.sin(camera.rotationY)
            camera.z += math.cos(camera.rotationY)

    # move the camera to the correct position, which means
    # updating the view stack
    ms.rotateX(ms.MatrixStack.view,
               camera.rotationX)
    ms.rotateY(ms.MatrixStack.view,
               -camera.rotationY)
    ms.translate(ms.MatrixStack.view,
                 -camera.x,
                 -camera.y,
                 -camera.z)

    # render the models

    triangle.render()

    MAX_VERTEX_BUFFER = 512 * 1024
    MAX_ELEMENT_BUFFER = 128 * 1024


    if(nuklear.begin(title="Demonstration",
                     bounds=nk.Rect(10.0,10.0,230.0,250.0),
                     flags=nk.WINDOW_BORDER
                       |nk.WINDOW_MOVABLE
                       |nk.WINDOW_SCALABLE
                       |nk.WINDOW_MINIMIZABLE
                       |nk.WINDOW_TITLE)):

        nuklear.layout_row_static(height=30.0,
                                  item_width=80,
                                  cols=5)
        if nuklear.button_label(title="button"):
            print('button pressed')

        nuklear.layout_row_dynamic(30.0, 2)

        # simulate a local static variable
        try:
            op
        except Exception:
            op = 0

        if nuklear.option_label(label="easy",
                                active= op == 0): op = 0
        if nuklear.option_label(label="hard",
                                active= op == 1): op = 1

        nuklear.layout_row_dynamic(25.0, 1)

        # simulate a local static variable
        try:
            prop
        except Exception:
            prop = 20

        prop = nuklear.property_int(name="Compression:",
                                    minV=0,
                                    val=prop,
                                    maxV=100,
                                    step=10,
                                    inc_per_pixel=1)

        nuklear.layout_row_dynamic(20.0, 1)
        nuklear.label(text="background:",
                      alignment=nk.TEXT_LEFT)

        # simulate a local static variable
        try:
            background
        except Exception:
            background = nk.Color(0, 0, 0, 255)

        nuklear.layout_row_dynamic(25.0, 1)
        if nuklear.combo_begin_color(color=background,
                                     size=nk.Vec2(nuklear.widget_width(),
                                                  400)):
            nuklear.layout_row_dynamic(120.0, 1)
            background = nuklear.color_picker(color=background,
                                              format=nk.RGBA)

            nuklear.layout_row_dynamic(25.0, 1)
            background.r = nuklear.propertyi(name="#R:",
                                             minVal=0,
                                             val=background.r,
                                             maxVal=255,
                                             step=1,
                                             inc_per_pixel=1.0)
            background.g = nuklear.propertyi(name="#G:",
                                             minVal=0,
                                             val=background.g,
                                             maxVal=255,
                                             step=1,
                                             inc_per_pixel=1.0)
            background.b = nuklear.propertyi(name="#B:",
                                             minVal=0,
                                             val=background.b,
                                             maxVal=255,
                                             step=1,
                                             inc_per_pixel=1.0)
            background.a = nuklear.propertyi(name="#A:",
                                             minVal=0,
                                             val=background.a,
                                             maxVal=255,
                                             step=1,
                                             inc_per_pixel=1.0)


            gl.glClearColor(background.r/255,background.g/255,background.b/255,background.a/255)

            nuklear.combo_end()

    nuklear.end()



    # show overview

    # simulate a local static variable
    try:
        show_menu
    except Exception:
        show_menu = True
    try:
        titlebar
    except Exception:
        titlebar  = True
    try:
        border
    except Exception:
        border = True
    try:
        resize
    except Exception:
        resize = True
    try:
        movable
    except Exception:
        movable = True
    try:
        no_scrollbar
    except Exception:
        no_scrollbar = False
    try:
        scale_left
    except Exception:
        scale_left = False
    try:
        minimizable
    except Exception:
        minimizable = True



    window_flags = 0
    #TODO -- map the ctx struct

    #ctx->style.window.header.align = header_align

    if(border) : window_flags |= nk.WINDOW_BORDER
    if(resize) : window_flags |= nk.WINDOW_SCALABLE
    if(movable) : window_flags |= nk.WINDOW_MOVABLE
    if(no_scrollbar) : window_flags |= nk.WINDOW_NO_SCROLLBAR
    if(scale_left) : window_flags |= nk.WINDOW_SCALE_LEFT
    if(minimizable) : window_flags |= nk.WINDOW_MINIMIZABLE


    if nuklear.begin(title="Overview",
                     bounds=nk.Rect(10,300,400,600),
                     flags=window_flags):
        if show_menu:
            try:
                mprog
            except Exception:
                mprog = 60
            try:
                mslider
            except Exception:
                mslider = 10
            try:
                mcheck
            except Exception:
                mcheck = False

            try:
                show_app_about
            except Exception:
                show_app_about = False

            nuklear.menubar_begin()
            nuklear.layout_row_begin(fmt=nk.STATIC,
                                     row_height=25.0,
                                     cols=5)
            nuklear.layout_row_push(ratio_or_width=45.0)
            if nuklear.menu_begin_label(text="MENU",
                                        align=nk.TEXT_LEFT,
                                        size=nk.Vec2(120,120)):
                nuklear.layout_row_dynamic(25.0, 1)
                if nuklear.menu_item_label(label="Hide",
                                           align=nk.TEXT_LEFT):
                    show_menu = False
                if nuklear.menu_item_label(label="About",
                                           align=nk.TEXT_LEFT):
                    show_app_about = True
                (modified,mprog) = nuklear.progress(cur=mprog,
                                                    max=100,
                                                    is_modifyable=nk.MODIFIABLE)
                (modified,mslider) = nuklear.slider_int(minV=0,
                                                        value=mslider,
                                                        maxV=16,
                                                        step=1)
                # TODO, for some reason, this checkbox is not showing.
                # if i move it up 2 lines, it does, and another widget
                # is not showing
                (modified,mcheck) = nuklear.checkbox_label(text="check",
                                                           active=mcheck)

                nuklear.menu_end()
            nuklear.layout_row_push(ratio_or_width=60.0)
            if nuklear.menu_begin_label(text="Advanced",
                                        align=nk.TEXT_LEFT,
                                        size=nk.Vec2(200,600)):
                # TODO -- do the advanced menu

                nuklear.menu_end()

            nuklear.layout_row_push(70.0)
            (modified,mprog) = nuklear.progress(cur=mprog,
                                                 max=100,
                                                 is_modifyable=nk.MODIFIABLE)
            (modified,mslider) = nuklear.slider_int(minV=0,
                                                    value=mslider,
                                                    maxV=16,
                                                    step=1)
            (modified,mcheck) = nuklear.checkbox_label(text="check",
                                                       active=mcheck)

            nuklear.menubar_end()

            if show_app_about:
                if nuklear.popup_begin(theType=nk.POPUP_STATIC,
                                       title="About",
                                       flags=nk.WINDOW_CLOSABLE,
                                       rect=nk.Rect(20,100,400,200)):
                    nuklear.layout_row_dynamic(20.0, 1)
                    nuklear.label(text="pyNuklear",
                                  alignment=nk.TEXT_LEFT)
                    nuklear.label(text="By William Emerison Six",
                                  alignment=nk.TEXT_LEFT)
                    nuklear.label(text="pyNuklear is MIT-licensed.",
                             alignment=nk.TEXT_LEFT)
                    nuklear.label(text="based on Nuklear",
                                  alignment=nk.TEXT_LEFT)
                    nuklear.label(text="By Micha Mettke",
                                  alignment=nk.TEXT_LEFT)
                    nuklear.label(text="nuklear is licensed under the public domain License.",
                             alignment=nk.TEXT_LEFT)

                    nuklear.popup_end()
                else:
                    show_app_about = False
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Window",
                                 state=nk.MINIMIZED) :
                nuklear.layout_row_dynamic(30.0, 2)
                (modified,titlebar) = nuklear.checkbox_label(text="Titlebar",
                                                             active=titlebar)
                (modified,show_menu) = nuklear.checkbox_label(text="Menu",
                                                              active=show_menu)
                (modified,border) = nuklear.checkbox_label(text="Border",
                                                           active=border)
                (modified,resize) = nuklear.checkbox_label(text="Resizable",
                                                           active=resize)
                (modified,movable) = nuklear.checkbox_label(text="Movable",
                                                            active=movable)
                (modified,no_scrollbar) = nuklear.checkbox_label(text="No Scrollbar",
                                                                 active=no_scrollbar)
                (modified,minimizable) = nuklear.checkbox_label(text="Minimizable",
                                                                active=minimizable)
                (modified,scale_left) = nuklear.checkbox_label(text="Scale Left",
                                                               active=scale_left)
                nuklear.tree_pop()
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Widgets",
                                 state=nk.MINIMIZED) :
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Text",
                                     state=nk.MINIMIZED) :
                    nuklear.layout_row_dynamic(20.0 ,1)
                    nuklear.label(text="Label aligned left",
                                  alignment=nk.TEXT_LEFT)
                    nuklear.label(text="Label aligned centered",
                                  alignment=nk.TEXT_CENTERED)
                    nuklear.label(text="Label aligned right",
                                  alignment=nk.TEXT_RIGHT)
                    nuklear.label_colored(text="Blue text",
                                          align=nk.TEXT_LEFT,
                                          color=nk.Color(0,0,255,255))
                    nuklear.label_colored(text="Yellow text",
                                          align=nk.TEXT_LEFT,
                                          color=nk.Color(255,255,0,255))
                    nuklear.text(text="Text without /0",
                                 length=15,
                                 alignment=nk.TEXT_ALIGN_RIGHT)
                    nuklear.layout_row_static(height=100.0,
                                              item_width=200,
                                              cols=1)
                    nuklear.label_wrap(text="This is a very long line to hopefully get this text to be wrapped into multiple lines to show line wrapping")
                    nuklear.layout_row_dynamic(100.0, 1)
                    nuklear.label_wrap(text="This is another long text to show dynamic window changes on multiline text")

                    nuklear.tree_pop()
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Button",
                                     state=nk.MINIMIZED) :
                    nuklear.layout_row_static(height=30,
                                              item_width=100,
                                              cols=3)
                    if nuklear.button_label(title="Button"):
                        print("Button pressed!")
                    nuklear.button_set_behavior(nk.BUTTON_REPEATER)
                    if nuklear.button_label(title="Repeater"):
                        print("Repeater is being pressed!")
                    nuklear.button_set_behavior(nk.BUTTON_DEFAULT)
                    if nuklear.button_color(nk.Color(0,0,255,255)):
                        pass
                    nuklear.layout_row_static(height=25.0,
                                              item_width=25,
                                              cols=8)
                    nuklear.button_symbol(nk.SYMBOL_CIRCLE_SOLID)
                    nuklear.button_symbol(nk.SYMBOL_CIRCLE_OUTLINE)
                    nuklear.button_symbol(nk.SYMBOL_RECT_SOLID)
                    nuklear.button_symbol(nk.SYMBOL_RECT_OUTLINE)
                    nuklear.button_symbol(nk.SYMBOL_TRIANGLE_UP)
                    nuklear.button_symbol(nk.SYMBOL_TRIANGLE_DOWN)
                    nuklear.button_symbol(nk.SYMBOL_TRIANGLE_LEFT)
                    nuklear.button_symbol(nk.SYMBOL_TRIANGLE_RIGHT)

                    nuklear.layout_row_static(height=30.0,
                                              item_width=100,
                                              cols=2)
                    nuklear.button_symbol_label(symbol=nk.SYMBOL_TRIANGLE_LEFT,
                                                label="prev",
                                                align=nk.TEXT_RIGHT)
                    nuklear.button_symbol_label(symbol=nk.SYMBOL_TRIANGLE_RIGHT,
                                                label="next",
                                                align=nk.TEXT_LEFT)
                    nuklear.tree_pop()
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Basic",
                                     state=nk.MINIMIZED) :
                    nuklear.layout_row_static(height=30.0,
                                              item_width=100,
                                              cols=1)
                    try:
                        basicCheckBox
                    except Exception:
                        basicCheckBox = False
                    (modified,basicCheckBox) = nuklear.checkbox_label(text="CheckBox",
                                                                      active=basicCheckBox)

                    nuklear.layout_row_static(height=30.0,
                                              item_width=80,
                                              cols=3)

                    A = 1
                    B = 2
                    C = 3
                    try:
                        basicOption
                    except Exception:
                        basicOption = A

                    if nuklear.option_label(label="optionA",
                                            active= basicOption == A): basicOption = A
                    if nuklear.option_label(label="optionB",
                                            active= basicOption == B): basicOption = B
                    if nuklear.option_label(label="optionC",
                                            active= basicOption == C): basicOption = C


                    #TODO -- figure out why this code isn't working quite correctly
                    # nuklear.layout_row(layout_format=nk.STATIC,
                    #                    height=30.0,
                    #                    cols=2,
                    #                    ratio=[120.0,150.0])
                    # once I figure that out, delete the subsequent 3 lines
                    nuklear.layout_row_static(height=30.0,
                                              item_width=100,
                                              cols=2)
                    try:
                        basicSlider
                    except Exception:
                        basicSlider = 5
                    nuklear.label(text="Slider Int",
                                  alignment=nk.TEXT_LEFT)
                    (modified,basicSlider) = nuklear.slider_int(minV=0,
                                                                value=basicSlider,
                                                                maxV=10,
                                                                step=1)
                    try:
                        floatSlider
                    except Exception:
                        floatSlider = 2.5
                    nuklear.label(text="Slider Float",
                                  alignment=nk.TEXT_LEFT)
                    (modified,floatSlider) = nuklear.slider_float(minV=0.0,
                                                                  value=floatSlider,
                                                                  maxV=5.0,
                                                                  step=0.5)


                    nuklear.tree_pop()
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Selectable",
                                     state=nk.MINIMIZED) :

                    nuklear.tree_pop()
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Combo",
                                     state=nk.MINIMIZED) :
                    nuklear.tree_pop()
                if nuklear.tree_push(theType=nk.TREE_NODE,
                                     title="Input",
                                     state=nk.MINIMIZED) :
                    nuklear.tree_pop()

                nuklear.tree_pop()
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Chart",
                                 state=nk.MINIMIZED,) :
                #TODO
                nuklear.tree_pop()
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Chart",
                                 state=nk.MINIMIZED) :
                #TODO
                nuklear.tree_pop()
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Popup",
                                 state=nk.MINIMIZED) :
                #TODO
                nuklear.tree_pop()
            if nuklear.tree_push(theType=nk.TREE_TAB,
                                 title="Layout",
                                 state=nk.MINIMIZED) :
                #TODO
                nuklear.tree_pop()


    nuklear.end()

    nk.glfw3_render(nk.ANTI_ALIASING_ON, MAX_VERTEX_BUFFER, MAX_ELEMENT_BUFFER)

    # done with frame, flush and swap buffers
    # Swap front and back buffers
    glfw.glfwSwapBuffers(window)


glfw.glfwTerminate()
