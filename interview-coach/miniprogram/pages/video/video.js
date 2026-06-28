Page({
  data: {
    id: 0,
    name: '',
    videoUrl: '',
    codeCard: '',
    approach: '即将上线',
    complexity: '即将上线',
    goldLine: '',
    commentPrompt: '你觉得这道题用哪种方法最好？',
  },

  onLoad(options) {
    const id = parseInt(options.id) || 0;
    const name = decodeURIComponent(options.name || '');
    wx.setNavigationBarTitle({ title: `#${id} ${name}` });

    // 根据题目ID加载对应的元数据
    const meta = this.getQuestionMeta(id);
    this.setData({
      id, name,
      videoUrl: meta.videoUrl,
      codeCard: meta.codeCard,
      approach: meta.approach,
      complexity: meta.complexity,
      goldLine: meta.goldLine,
      commentPrompt: meta.commentPrompt,
    });
  },

  getQuestionMeta(id) {
    // 已发布的12题元数据
    const metaMap = {
      1: { approach: '哈希表一次遍历', complexity: 'O(n) / O(n)', goldLine: '用空间换时间，哈希表存已遍历值', videoUrl: '/videos/lc001-两数之和/lc001-两数之和.mp4', codeCard: '/covers/lc001-code-card.png', commentPrompt: '你第一次做用了暴力双循环还是哈希表？' },
      2: { approach: '模拟加法进位', complexity: 'O(max(n,m)) / O(1)', goldLine: '进位是链表加法的灵魂', videoUrl: '/videos/lc002-两数相加/lc002-两数相加.mp4', codeCard: '/covers/lc002-code-card.png', commentPrompt: '你处理进位用了if还是while？' },
      3: { approach: '滑动窗口+哈希集', complexity: 'O(n) / O(k)', goldLine: '窗口向右滑动，重复就缩左边界', videoUrl: '/videos/lc003-无重复最长子串/lc003-无重复最长子串.mp4', codeCard: '/covers/lc003-code-card.png', commentPrompt: '你用的Set还是Map来存窗口字符？' },
      11: { approach: '双指针向中间收缩', complexity: 'O(n) / O(1)', goldLine: '短板决定容量，哪边短就移动哪边', videoUrl: '/videos/lc011-盛最多水的容器/lc011-盛最多水的容器.mp4', codeCard: '/covers/lc011-code-card.png', commentPrompt: '你一开始想到双指针还是暴力？' },
      15: { approach: '排序+双指针去重', complexity: 'O(n²) / O(1)', goldLine: '排序后固定一个，双指针扫剩下', videoUrl: '/videos/lc015-三数之和/lc015-三数之和.mp4', codeCard: '/covers/lc015-code-card.png', commentPrompt: '去重逻辑你放在循环里还是循环外？' },
      21: { approach: '双指针合并+哑节点', complexity: 'O(n+m) / O(1)', goldLine: 'dummy头节点省去特殊情况处理', videoUrl: '/videos/lc021-合并两个有序链表/lc021-合并两个有序链表.mp4', codeCard: '/covers/lc021-code-card.png', commentPrompt: '你用迭代法还是递归法合并？' },
      128: { approach: '哈希集+连续序列计数', complexity: 'O(n) / O(n)', goldLine: '只从序列起点开始数，避免重复扫描', videoUrl: '/videos/lc128-最长连续序列/lc128-最长连续序列.mp4', codeCard: '/covers/lc128-code-card.png', commentPrompt: '你想到了Set去重+只从起点数吗？' },
      141: { approach: '快慢指针判环', complexity: 'O(n) / O(1)', goldLine: '快慢指针相遇，必有环', videoUrl: '/videos/lc141-环形链表/lc141-环形链表.mp4', codeCard: '/covers/lc141-code-card.png', commentPrompt: '你能用哈希表和快慢指针分别实现吗？' },
      160: { approach: '双指针对齐遍历', complexity: 'O(n+m) / O(1)', goldLine: '走到尽头换条路，终会相遇', videoUrl: '/videos/lc160-相交链表/lc160-相交链表.mp4', codeCard: '/covers/lc160-code-card.png', commentPrompt: '你用的双指针浪漫相遇还是哈希集？' },
      206: { approach: '迭代/递归反转指针', complexity: 'O(n) / O(1)', goldLine: '每走一步，翻转一个箭头方向', videoUrl: '/videos/lc206-反转链表/lc206-反转链表.mp4', codeCard: '/covers/lc206-code-card.png', commentPrompt: '你习惯递归还是迭代反转？' },
      234: { approach: '快慢指针找中点+反转后半段', complexity: 'O(n) / O(1)', goldLine: '找中点，反转后半，逐一比较', videoUrl: '/videos/lc234-回文链表/lc234-回文链表.mp4', codeCard: '/covers/lc234-code-card.png', commentPrompt: '你用栈比较还是原地反转比较？' },
      283: { approach: '双指针交换+0后置', complexity: 'O(n) / O(1)', goldLine: '慢指针标记非零区域边界', videoUrl: '/videos/lc283-移动零/lc283-移动零.mp4', codeCard: '/covers/lc283-code-card.png', commentPrompt: '你用交换法还是先填后补零？' },
    };

    return metaMap[id] || {
      approach: '即将上线', complexity: '即将上线', goldLine: '',
      videoUrl: '', codeCard: '', commentPrompt: '你期待这道题的动画讲解吗？',
    };
  },
});
