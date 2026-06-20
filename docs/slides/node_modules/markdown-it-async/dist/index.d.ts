import MarkdownIt, { Options, PresetName } from 'markdown-it';
export { PluginSimple, PluginWithOptions, PluginWithParams } from 'markdown-it';

interface MarkdownItAsyncOptions extends Omit<Options, 'highlight'> {
    /**
     * Highlighter function for fenced code blocks.
     * Highlighter `function (str, lang, attrs)` should return escaped HTML. It can
     * also return empty string if the source was not changed and should be escaped
     * externally. If result starts with <pre... internal wrapper is skipped.
     * @default null
     */
    highlight?: ((str: string, lang: string, attrs: string) => string | Promise<string>) | null | undefined;
}

type MarkdownItASyncPlaceholderMap = Map<string, [promise: Promise<string>, str: string, lang: string, attrs: string]>;
declare class MarkdownItAsync extends MarkdownIt {
    map: MarkdownItASyncPlaceholderMap;
    constructor(presetName: PresetName, options?: MarkdownItAsyncOptions);
    constructor(options?: MarkdownItAsyncOptions);
    renderAsync(src: string, env?: any): Promise<string>;
}
declare function createMarkdownItAsync(presetName: PresetName, options?: MarkdownItAsyncOptions): MarkdownItAsync;
declare function createMarkdownItAsync(options?: MarkdownItAsyncOptions): MarkdownItAsync;
declare function replaceAsync(string: string, searchValue: RegExp, replacer: (...args: string[]) => Promise<string>): Promise<string>;

export { type MarkdownItASyncPlaceholderMap, MarkdownItAsync, type MarkdownItAsyncOptions, type MarkdownItAsyncOptions as Options, createMarkdownItAsync, createMarkdownItAsync as default, replaceAsync };
