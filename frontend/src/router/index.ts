import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { getToken } from "../utils/token";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    component: () => import("../views/login/LoginView.vue"),
    meta: { public: true },
  },
  // 用户端
  {
    path: "/user",
    component: () => import("../layouts/UserLayout.vue"),
    meta: { requiresAuth: true, roles: ["user"] },
    children: [
      { path: "", redirect: "/user/chat" },
      { path: "chat", component: () => import("../views/chat/ChatView.vue") },
      { path: "mental/analyze", component: () => import("../views/mental/MentalAnalyzeView.vue") },
      { path: "profile", component: () => import("../views/profile/ProfileView.vue") },
    ],
  },
  // 管理员端
  {
    path: "/admin",
    component: () => import("../layouts/AdminLayout.vue"),
    meta: { requiresAuth: true, roles: ["admin"] },
    children: [
      { path: "", redirect: "/admin/knowledge/manage" },
      {
        path: "knowledge/manage",
        component: () => import("../views/knowledge/KnowledgeManageView.vue"),
      },
      {
        path: "users",
        component: () => import("../views/admin/UserManageView.vue"),
      },
    ],
  },
  // 根路径按角色跳转——完全由 beforeEach 守卫处理，不设 redirect
  {
    path: "/",
    component: { template: "<div />" },
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    component: () => import("../views/error/NotFoundView.vue"),
    meta: { public: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  if (to.meta.public) return true;

  const token = getToken();
  if (!token) return "/login";

  const authStore = useAuthStore();
  if (!authStore.user) {
    try {
      await authStore.fetchMe();
    } catch {
      authStore.logout();
      return "/login";
    }
  }

  // 根路径按角色跳转
  if (to.path === "/") {
    return authStore.user?.role === "admin" ? "/admin" : "/user/chat";
  }

  // 路由声明了允许的角色列表时，检查当前用户角色
  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && authStore.user) {
    if (!allowedRoles.includes(authStore.user.role)) {
      // 角色不匹配：用户误入管理端 → 回用户首页；管理员误入用户端 → 回管理首页
      return authStore.user.role === "admin" ? "/admin" : "/user/chat";
    }
  }

  return true;
});

export default router;