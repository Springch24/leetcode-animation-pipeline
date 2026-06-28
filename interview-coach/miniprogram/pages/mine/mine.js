Page({
  data: {
    historyCount: 0,
    savedCount: 0,
    videoWatched: 0,
  },
  onShow() {
    const history = wx.getStorageSync('search_history') || [];
    const saved = wx.getStorageSync('saved_questions') || [];
    const watched = wx.getStorageSync('watched_videos') || [];
    this.setData({
      historyCount: history.length,
      savedCount: saved.length,
      videoWatched: watched.length,
    });
  },
  goHistory() { wx.showToast({ title: '即将上线', icon: 'none' }); },
  goSaved() { wx.showToast({ title: '即将上线', icon: 'none' }); },
  goAbout() {
    wx.showModal({
      title: '面试逆推器',
      content: '输入目标公司+岗位，2秒获取高频面经题清单。已有视频直接看动画讲解。\n\n数据来源: LeetcodeTop 面经高频汇总\n视频制作: 全自动动画流水线',
      showCancel: false,
    });
  },
});
