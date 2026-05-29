# lnjx2025 — 爆破工程管理系统

企业级爆破工程人员/证件/现场记录管理系统，基于 Django + MySQL + PWA。

## 版本记录

### v1.8 — 手机端侧边栏修复 + 员工管理改造

**手机端侧边栏触摸修复（home.html）**
- 修复手机端（≤991px）侧边栏"一碰就缩回"和"触摸穿透"问题
- **坑：bg-overlay 的 `z-index: 999` 高于 sidebar-wrapper 的 `z-index: 9`**，遮罩层物理覆盖侧边栏，所有触摸被拦截后触发关闭
- **坑：只拦了 `touchstart` 没拦 `touchend`**，浏览器合成 click 照常触发关闭
- **坑：SimpleBar 内部 `pointer-events: none`** 导致触摸穿透
- **坑：SimpleBar 与原生滚动双滚动冲突**
- 修复：z-index 提到 1000、事件拦截扩展到 click+touchend+touchmove、修复指针穿透、手机端禁用 SimpleBar

**员工管理改造**
- 路由迁移：`/staff_list/` → `/home/admin/`，`/staff/` → `/home/staff/`，`/staff_cert/` → `/home/staff_cert/`
- 添加员工表单字段改为 ident/username/role/password/department
- 修正同名函数冲突

**卡片页面布局改造**
- `/home/mine_card/` 全面重写为左右对称布局
- Excel 拖拽导入、姓名自动补全、工种下拉选择、照片拖拽上传

### v1.7 — badge 排序修复
### v1.6 — PWA 离线推送
### v1.5 — PWA 离线页面 + 推送通知
### v1.4 — 签名智能识别
### v1.3 — 手写评分
### v1.2 — SQLite → MySQL 迁移
### v1.1 — 路由重构
### v1.0 — 初始版本
