# coding: utf-8

# common defines
block_element_tags = (
    'div', 'article', 'section', 'table', 'ul', 'ol', 'p', 'td', 'dl'
)
self_closing_tags = (
    'br', 'hr', 'img', 'col', 'source', 'embed', 'param'
)
media_element_tags = ('video', 'audio', 'object', 'embed', 'iframe')
source_element_tags = ('img', 'video', 'audio', 'object', 'embed', 'iframe')
useless_tags = ('form', 'fieldset', 'font')

img_lazy_srcs = (
    'data-src',
    'data-actualsrc',
    'data-original',
    'data-original-src',
)
positive_symbols = ('article', 'post', 'content', 'entry')

# pre clean configurations

min_length_of_paragraph = 20

# span tag can not have too many classes
max_length_of_class = 25

force_keep_symbols = (
    'with-sidebar',
    'comments-open',
    'comments-closed',
    'content',
    'main',
    'post',
    'article'
)

ignored_symbols = (
    'carousel',
    'comment',
    'comments',
    'adblk',
    'instapaper_ignore',
    'languages',
    'toc',
)
ignored_prefix_symbols = (
    'ad-',
    'ad_',
    'google_ads_',
)
ignored_suffix_symbols = (
    '_ad',
    '-ad',
)
ignored_in_content = (
    'hide',
    'hidden',
)

# if negative node has a too long text, we should keep it
min_negative_text_length = 120
negative_symbols = (
    'side',
    'sub-',
    'sub_',
    'subcontent',
    'bar',
    'button',
    'btn',
    'navi',
    'prev',
    'next',
    'foot-',
    'foot_',
    'footer',

    'tags',
    'tag',
    'share',
    'bshare',
    'bdshare',
    'sharing',
    'WPSNS',
    'wpl-likebox ',
    'read_later ',
    'digg',
    'recommend',
    'recowrap',

    'comment',
    'related',
    'refer',
    'vote',
    'rss',
    'subscribe',
    'newsletter',
)

negative_sources = (
    '/ad/',
    '/ad.',
    '.ad.',

    'g.csdn.net',
    '.adsfactor.net',
    '.allyes.com',

    '.2mdn.net',
    'adbrite.com',
    'adbureau.net',
    'admob.com',
    '.adpolestar.net',
    'advertising.com',
    'adzerk.net',
    'atdmt.com',
    'adg.nextag.com',
    'bannersxchange.com',
    'buysellads.com',
    'content.aimatch.com',
    'de17a.com',
    'doubleclick.net',
    'googlesyndication.com',
    'impact-ad.jp',
    'itmedia.jp',
    'microad.jp',
    'serving-sys.com',
    'feedsky.com',
    'addthis.org',
    'wumii.com',
    'printfriendly.com',
    'chanet.com.cn',
)

positive_sources = (
    'tudou.com',
    'youku.com',
    'tv.sohu.com',
    'video.sina.com.cn',
    'swf.ws.126.net/movieplayer/',
    'player.letvcdn.com',
    'qiyi.com/player/',
    'img.hexun.com/swf/',
    'img.ifeng.com/swf/',
    'imgcache.qq.com/tencentvideo',
    'player.ku6cdn.com',
    '.slideshare.net',
    'vine.co',
    'video.ted.com',
    'youtube.com',
    'youtube-nocookie.com',
    'vimeo.com',
    'hulu.com',
    'yahoo.com',
    'flickr.com',
    'newsnetz.ch',
    '/media/',
)

related_content_text = (
    '相关文章',
    '相关新闻',
    '相关链接',
    '更多阅读',
    '延伸阅读',
    '扩展阅读',
    '精彩推荐',
    '精选推荐',
    '编辑推荐',
    '关于作者',
    '讨论',
    '你还可能感兴趣',
    '喜欢这篇文章',
    '本文相关推荐',
    '分享',
    '打印',
    'relatedposts',
    'relevantposts',
    'similarposts',
    'comments',
    'commentlist',
    'Related',
)


# guess configurations

content_container_tags = ('div', 'section', 'article', 'td')
max_depth_of_candidate = 20
min_content_length = 200
min_diff_of_point = 2


# post clean configurations
keep_attributes = (
    'data-attachement',
    'data-flex',
)

elements_keep_attributes = {
    'a': ('href', 'title', 'name'),
    'img': ('src', 'width', 'height', 'alt', 'title'),

    'video': ('src', 'width', 'height', 'poster', 'audio', 'preload',
              'autoplay', 'loop', 'controls'),
    'audio': ('src', 'preload', 'autoplay', 'loop', 'controls'),
    'source': ('src', 'type'),
    'track': ('default', 'kind', 'label', 'src', 'srclang'),

    'object': ('data', 'type', 'width', 'height', 'classid', 'codebase',
               'codetype'),
    'param': ('name', 'value'),
    'embed': ('src', 'type', 'width', 'height', 'flashvars',
              'allowscriptaccess', 'allowfullscreen', 'bgcolor'),

    'iframe': ('src', 'width', 'height', 'frameborder', 'scrolling'),

    'td': ('colspan', 'rowspan'),
    'th': ('colspan', 'rowspan'),
}

ignored_bottom_symbols = (
    'disqus',
    'random',
    'tuijian',
    'jiathis',
    'wumii',
    'related-posts',
    'comments',
    'commentbox',
    'comment-list',
    'commentlist',
    'blog_comm',
    'author-box',
    'article-related',
    'metadata',
)

ignored_meta_symbols = (
    'author',
)
