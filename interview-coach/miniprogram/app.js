App({
  globalData: {
    userInfo: null,
    isSubscribed: false,
    selectedCompany: '',
    selectedRole: '',
    questionBank: null,
  },
  onLaunch() {
    // 加载题库
    try {
      const bank = require('./utils/question_bank.json');
      this.globalData.questionBank = bank;
      console.log(`题库加载: ${bank.total_questions} 题, ${bank.shipped_count} 有视频`);
    } catch (e) {
      console.error('题库加载失败', e);
    }
    // 获取用户设置
    const cached = wx.getStorageSync('user_settings');
    if (cached) {
      this.globalData.selectedCompany = cached.company || '';
      this.globalData.selectedRole = cached.role || '';
    }
  }
});
