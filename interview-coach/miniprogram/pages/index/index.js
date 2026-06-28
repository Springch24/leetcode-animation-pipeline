const app = getApp();

Page({
  data: {
    companies: [],
    selectedCompany: '',
    roles: [],
    selectedRole: '',
    totalQuestions: 0,
    shippedCount: 0,
  },

  onLoad() {
    const bank = app.globalData.questionBank;
    if (!bank) return;

    // 构建公司列表（只显示有数据的）
    const companyList = bank.company_list.filter(c => c.name !== '百度' && c.name !== '网易' && c.name !== '京东' && c.name !== '拼多多' && c.name !== '滴滴' && c.name !== '华为');
    const companies = companyList.map(c => ({
      name: c.name,
      questionCount: c.roles.reduce((sum, r) => {
        const qs = bank.companies[c.name]?.[r] || [];
        return sum + qs.length;
      }, 0),
    }));

    this.setData({
      companies,
      totalQuestions: bank.total_questions,
      shippedCount: bank.shipped_count,
    });

    // 恢复上次选择
    const cached = wx.getStorageSync('user_settings');
    if (cached && cached.company) {
      this.setData({ selectedCompany: cached.company });
      this.loadRoles(cached.company);
      if (cached.role) {
        this.setData({ selectedRole: cached.role });
      }
    }
  },

  selectCompany(e) {
    const company = e.currentTarget.dataset.company;
    this.setData({ selectedCompany: company, selectedRole: '' });
    this.loadRoles(company);
  },

  loadRoles(company) {
    const bank = app.globalData.questionBank;
    if (!bank) return;
    const cdata = bank.companies[company] || {};
    const roles = Object.keys(cdata).filter(r => cdata[r].length > 0);
    this.setData({ roles });
  },

  selectRole(e) {
    const role = e.currentTarget.dataset.role;
    this.setData({ selectedRole: role });
    // 保存选择
    wx.setStorageSync('user_settings', {
      company: this.data.selectedCompany,
      role,
    });
  },

  goSearch() {
    const { selectedCompany, selectedRole } = this.data;
    if (!selectedCompany || !selectedRole) {
      wx.showToast({ title: '请先选择公司和岗位', icon: 'none' });
      return;
    }
    wx.navigateTo({
      url: `/pages/result/result?company=${encodeURIComponent(selectedCompany)}&role=${encodeURIComponent(selectedRole)}`,
    });
  },
});
