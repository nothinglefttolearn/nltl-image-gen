# nltl image generation

Renders the nltl shapes, in the nltl colours, as images that look physically
made: printed, inked, on a material. Output is still images, mostly composited
into video elsewhere; this project never makes video itself.

## Language

### Effects

**Print**:
An effect that decides where ink lands within a shape. It can take ink away but never adds it beyond the shape's outline. Screenprint is a print.
_Avoid_: texture, coverage effect

**Surface**:
An effect that makes the whole image look like it is on a material, both the ink and the background. It changes colour only, never where ink is or how transparent anything is. Canvas is a surface.
_Avoid_: texture, substrate, finish

**Screenprint**:
A print where ink is pushed through a mesh by a squeegee. The ink runs out along the pull, leaving liquid-shaped gaps.

**Canvas**:
A surface that looks like artist's cotton canvas: a regular plain weave of slightly irregular threads. It shades colour lighter on the raised threads and darker between them.

**Flat**:
A render with no print and no surface: every ink pixel is exactly the shape's colour. It is what you get when no effects are chosen.
_Avoid_: cel-shaded, plain

**Weave**:
The spacing of a canvas's threads, as a fraction of the image edge.

### Repeatability

**Seed**:
The single number that fixes every random choice in a render. Every render has one, chosen at random when not given.

**Recipe**:
Everything needed to render an image again exactly: shape, colour, size, padding, background, each effect with its settings, and the seed. Every image carries its own recipe.
_Avoid_: config, settings, metadata

**Preset**:
A named, partial recipe meant for reuse: typically effects and their settings, never a seed. A preset can extend another preset, and explicit choices override it. A recipe is a record of one image; a preset is a starting point for many.
_Avoid_: style, template, profile

### Material

**Background**:
The colour of the material the shape is printed on. With no background the image is transparent outside the ink, and a surface then shows only on the ink.
_Avoid_: paper colour, base

**Ink**:
The shape's colour as it ends up on the image, after any print has decided where it goes.
