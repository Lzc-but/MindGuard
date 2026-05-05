<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const activeMenu = computed(() => route.path);

const menuItems = [
  { index: "/admin/knowledge/manage", label: "知识库管理", icon: "📚" },
];

const handleSelect = (index: string) => {
  router.push(index);
};

const handleLogout = () => {
  authStore.logout();
  ElMessage.success("已退出登录");
  router.push("/login");
};
</script>

<template>
  <div class="flex h-screen bg-[#f7f8fa] text-[#1d1d1f]">

    <!-- ===== 管理员侧边栏 ===== -->
    <aside class="flex flex-col w-[220px] bg-white border-r border-[#e5e7eb] shrink-0">
      <!-- Logo -->
      <div class="flex items-center h-14 px-4 border-b border-[#f0f0f0] shrink-0">
        <span class="text-lg font-bold text-[#4f6ef7] tracking-tight whitespace-nowrap">管理后台</span>
      </div>

      <!-- 菜单 -->
      <nav class="flex flex-col gap-0.5 px-2 py-3">
        <button
          v-for="item in menuItems"
          :key="item.index"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors"
          :class="activeMenu === item.index
            ? 'bg-[#eef1ff] text-[#4f6ef7] font-medium'
            : 'text-[#3a3a3c] hover:bg-[#f5f5f7]'"
          @click="handleSelect(item.index)"
        >
          <span class="text-lg shrink-0">{{ item.icon }}</span>
          <span class="whitespace-nowrap">{{ item.label }}</span>
        </button>
      </nav>
    </aside>

    <!-- ===== 右侧主区域 ===== -->
    <div class="flex flex-col flex-1 min-w-0">
      <!-- 顶部栏 -->
      <header class="flex items-center justify-between h-14 px-5 bg-white border-b border-[#e5e7eb] shrink-0">
        <span class="text-sm text-[#6e6e73]">
          管理员：<span class="text-[#1d1d1f] font-medium">{{ authStore.user?.username }}</span>
        </span>
        <button
          class="px-4 py-1.5 text-sm text-[#ff3b30] border border-[#ff3b30] rounded-lg hover:bg-red-50 transition-colors"
          @click="handleLogout"
        >退出登录</button>
      </header>

      <!-- 内容区 -->
      <main class="flex-1 min-h-0 overflow-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>