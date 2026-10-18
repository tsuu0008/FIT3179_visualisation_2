# Start here: three things to understand

## 1. HTML provides a place

```html
<div id="chart-04"></div>
```

This is an empty box with a unique name.

## 2. Vega-Embed inserts a chart

At the bottom of index.html, search for **INSERT THE CHARTS**:

```js
vegaEmbed("#chart-04", "charts/04_challenge_heatmap.json", {actions: false, renderer: "svg"});
```

Read it as: **draw this JSON chart inside this HTML box**.

- `#chart-04` matches the div id.
- The second argument is the chart file.
- `actions: false` hides the three-dot menu.
- `renderer: "svg"` draws a sharp vector chart.

This one-line function call is JavaScript, even though it is inside HTML. It is the only kind of JavaScript you need to read in this page.

The three scripts immediately above it load Vega, Vega-Lite and Vega-Embed. Loading those libraries does not insert a particular chart. The embed call does that. The JSON's `$schema` link identifies the JSON grammar; it does not load the drawing library.

## 3. JSON describes what to draw

Read these keys in order:

| Key | Plain meaning |
| --- | --- |
| data | Where are the records? |
| transform | Filter, count or calculate something. |
| mark | Draw a bar, point, line, shape or text. |
| encoding | Map fields to position, colour, size or text. |
| layer | Draw several things over one another. Later layers appear on top. |
| params | A value the reader can change, such as a grade. |
| config | Fonts, axes and legends. |

Start with chart 05: a rule and dot show each grade's median distance; a text layer adds its value. Then inspect chart 04: rectangles show counts, and text shows the same numbers.

Open the website through **Live Server**, not by double-clicking the HTML. JSON files can be edited directly; reload afterwards. No rebuild command is needed.
