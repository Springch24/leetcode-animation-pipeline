const app = getApp();

Page({
  data: {
    company: '',
    role: '',
    questions: [],
    filteredQuestions: [],
    videoCount: 0,
    filterDifficulty: '全部',
    filterVideo: '全部',
  },

  onLoad(options) {
    const company = decodeURIComponent(options.company || '');
    const role = decodeURIComponent(options.role || '');
    wx.setNavigationBarTitle({ title: `${company} · ${role}` });

    const bank = app.globalData.questionBank;
    if (!bank) {
      wx.showToast({ title: '数据加载失败', icon: 'none' });
      return;
    }

    const rawQuestions = bank.companies[company]?.[role] || [];
    const questions = rawQuestions.map(q => ({
      ...q,
      has_video: q.has_video || false,
      video_id: q.video_id || '',
    }));

    const videoCount = questions.filter(q => q.has_video).length;

    this.setData({
      company, role, questions,
      filteredQuestions: questions,
      videoCount,
    });
  },

  setFilter(e) {
    const { type, val } = e.currentTarget.dataset;
    const data = {};

    if (type === 'difficulty') {
      data.filterDifficulty = val;
    } else {
      data.filterVideo = val;
    }

    this.setData(data);
    this.applyFilters();
  },

  applyFilters() {
    let list = [...this.data.questions];
    const { filterDifficulty, filterVideo } = this.data;

    if (filterDifficulty !== '全部') {
      list = list.filter(q => q.difficulty === filterDifficulty);
    }
    if (filterVideo === '有视频') {
      list = list.filter(q => q.has_video);
    } else if (filterVideo === '待上线') {
      list = list.filter(q => !q.has_video);
    }

    this.setData({ filteredQuestions: list });
  },

  goVideo(e) {
    const { id, hasVideo } = e.currentTarget.dataset;
    if (!hasVideo) {
      wx.showToast({ title: '视频即将上线，敬请期待', icon: 'none' });
      return;
    }
    // 找到题目详情
    const q = this.data.questions.find(item => item.id === id);
    if (q && q.video_id) {
      wx.navigateTo({ url: `/pages/video/video?id=${id}&videoId=${q.video_id}&name=${encodeURIComponent(q.name)}` });
    }
  },
});
