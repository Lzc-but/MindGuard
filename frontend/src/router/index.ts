import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { getToken } from "../utils/token";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    component: () => import("../views/login/LoginView.vue"),
    meta: { public: true },
  },
  {
    path: "/",
    component: () => import("../layouts/MainLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      { path: "", redirect: "/chat" },
      { path: "chat", component: () => import("../views/chat/ChatView.vue") },
      { path: "mental/analyze", component: () => import("../views/mental/MentalAnalyzeView.vue") },
      {
        path: "knowledge/manage",
        component: () => import("../views/knowledge/KnowledgeManageView.vue"),
        meta: { roles: ["admin"] },
      },
      { path: "profile", component: () => import("../views/profile/ProfileView.vue") },
    ],
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

  const roles = to.meta.roles as string[] | undefined;
  if (roles && authStore.user && !roles.includes(authStore.user.role)) {
    return "/chat";
  }

  return true;
});

export default router;
