import MarkdownIt from 'markdown-it';

var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => {
  __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
  return value;
};
const placeholder = (id) => `<pre>::markdown-it-async::${id}::</pre>`;
const placeholderRe = /<pre>::markdown-it-async::(\w+)::<\/pre>/g;
function randStr() {
  return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
}
class MarkdownItAsync extends MarkdownIt {
  constructor(...args) {
    const map = /* @__PURE__ */ new Map();
    const options = args.length === 2 ? args[1] : args[0];
    if (options && "highlight" in options)
      options.highlight = wrapHightlight(options.highlight, map);
    super(...args);
    __publicField(this, "map");
    this.map = map;
  }
  async renderAsync(src, env) {
    const result = this.render(src, env);
    return replaceAsync(result, placeholderRe, async (match, id) => {
      if (!this.map.has(id))
        throw new Error(`Unknown highlight placeholder id: ${id}`);
      const [promise, _str, lang, _attrs] = this.map.get(id);
      const result2 = await promise || "";
      this.map.delete(id);
      if (result2.startsWith("<pre"))
        return result2;
      else
        return `<pre><code class="language-${lang}">${result2}</code></pre>`;
    });
  }
}
function createMarkdownItAsync(...args) {
  return new MarkdownItAsync(...args);
}
function replaceAsync(string, searchValue, replacer) {
  try {
    if (typeof replacer === "function") {
      const values = [];
      String.prototype.replace.call(string, searchValue, (...args) => {
        values.push(replacer(...args));
        return "";
      });
      return Promise.all(values).then((resolvedValues) => {
        return String.prototype.replace.call(string, searchValue, () => {
          return resolvedValues.shift() || "";
        });
      });
    } else {
      return Promise.resolve(
        String.prototype.replace.call(string, searchValue, replacer)
      );
    }
  } catch (error) {
    return Promise.reject(error);
  }
}
function wrapHightlight(highlight, map) {
  if (!highlight)
    return void 0;
  return (str, lang, attrs) => {
    const promise = highlight(str, lang, attrs);
    if (typeof promise === "string")
      return promise;
    const id = randStr();
    map.set(id, [promise, str, lang, attrs]);
    return placeholder(id);
  };
}

export { MarkdownItAsync, createMarkdownItAsync, createMarkdownItAsync as default, replaceAsync };
