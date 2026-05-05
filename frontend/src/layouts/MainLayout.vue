<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import { useChatStore } from "../stores/chat";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const chatStore = useChatStore();

const sidebarCollapsed = ref(false);
const activeMenu = computed(() => route.path);
const isChatRoute = computed(() => route.path.startsWith("/chat"));

const menuItems = computed(() => {
  const items = [
    { index: "/chat", label: "AI 聊天", icon: "💬" },
    { index: "/mental/analyze", label: "心理分析", icon: "🧠" },
    { index: "/profile", label: "个人信息", icon: "👤" },
  ];
  if (authStore.isAdmin) {
    items.splice(2, 0, { index: "/knowledge/manage", label: "知识库管理", icon: "📚" });
  }
  return items;
});

const handleSelect = (index: string) => {
  router.push(index);
};

const handleLogout = () => {
  authStore.logout();
  ElMessage.success("已退出登录");
  router.push("/login");
};

const goChatAndCreate = async () => {
  if (!isChatRoute.value) {
    await router.push("/chat");
  }
  await chatStore.createNewConversation();
};

const selectConversation = async (conversationId: string) => {
  if (!isChatRoute.value) {
    await router.push("/chat");
  }
  await chatStore.selectConversation(conversationId);
};

onMounted(async () => {
  await chatStore.refreshConversations();
  if (chatStore.conversations.length && !chatStore.currentConversationId) {
    await chatStore.selectConversation(chatStore.conversations[0].id);
  }
});
</script>

<template>
  <div class="flex h-screen bg-[#f7f8fa] text-[#1d1d1f]">

    <!-- ===== 可折叠侧边栏 ===== -->
    <aside
      class="flex flex-col bg-white border-r border-[#e5e7eb] transition-all duration-300 ease-in-out shrink-0"
      :class="sidebarCollapsed ? 'w-[64px]' : 'w-[240px]'"
    >
      <!-- Logo & 折叠按钮 -->
      <div class="flex items-center h-14 px-3 border-b border-[#f0f0f0] shrink-0"
        :class="sidebarCollapsed ? 'justify-center' : 'justify-between'"
      >
        <span
          v-show="!sidebarCollapsed"
          class="text-lg font-bold text-[#4f6ef7] tracking-tight whitespace-nowrap"
        >心护AI</span>
        <button
          class="flex items-center justify-center w-8 h-8 rounded-lg text-[#8e8e93] hover:bg-[#f5f5f7] hover:text-[#1d1d1f] transition-colors shrink-0"
          @click="sidebarCollapsed = !sidebarCollapsed"
          :title="sidebarCollapsed ? '展开侧栏' : '收起侧栏'"
        >
          <svg class="w-5 h-5 transition-transform duration-300" :class="sidebarCollapsed ? '' : 'rotate-180'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      <!-- 会话列表区域（仅聊天页可见） -->
      <div v-if="isChatRoute" class="flex flex-col flex-1 min-h-0 px-2 pt-3">
        <!-- 新对话按钮 -->
        <button
          v-if="!sidebarCollapsed"
          class="w-full mb-3 py-2.5 px-3 text-sm font-medium text-white bg-[#4f6ef7] hover:bg-[#3d5ce5] rounded-xl transition-colors shrink-0"
          @click="goChatAndCreate"
        >
          + 新对话
        </button>
        <button
          v-else
          class="flex items-center justify-center w-10 h-10 mx-auto mb-3 rounded-xl text-white bg-[#4f6ef7] hover:bg-[#3d5ce5] transition-colors shrink-0"
          @click="goChatAndCreate"
          title="新对话"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>

        <!-- 会话列表 -->
        <div v-show="!sidebarCollapsed" class="flex-1 min-h-0 overflow-y-auto space-y-1.5 pr-0.5 scrollbar-thin">
          <div
            v-for="item in chatStore.conversations"
            :key="item.id"
            class="group flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-colors"
            :class="item.id === chatStore.currentConversationId
              ? 'bg-[#eef1ff] text-[#4f6ef7]'
              : 'hover:bg-[#f5f5f7] text-[#3a3a3c]'"
            @click="selectConversation(item.id)"
          >
            <span class="text-sm truncate flex-1 min-w-0">{{ item.title }}</span>
            <div class="hidden group-hover:flex items-center gap-0.5 ml-1 shrink-0">
              <button
                class="p-1 rounded-md text-[#8e8e93] hover:text-[#4f6ef7] hover:bg-white transition-colors"
                title="重命名"
                @click.stop="chatStore.promptRenameConversation(item)"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <button
                class="p-1 rounded-md text-[#8e8e93] hover:text-red-500 hover:bg-white transition-colors"
                title="删除"
                @click.stop="chatStore.removeConversation(item.id)"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-show="!sidebarCollapsed" class="h-px bg-[#f0f0f0] my-2 shrink-0" />
      </div>

      <!-- 菜单 -->
      <nav class="flex flex-col gap-0.5 px-2 py-3 shrink-0">
        <button
          v-for="item in menuItems"
          :key="item.index"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors"
          :class="[
            activeMenu === item.index
              ? 'bg-[#eef1ff] text-[#4f6ef7] font-medium'
              : 'text-[#3a3a3c] hover:bg-[#f5f5f7]',
            sidebarCollapsed ? 'justify-center' : ''
          ]"
          @click="handleSelect(item.index)"
          :title="sidebarCollapsed ? item.label : ''"
        >
          <span class="text-lg shrink-0">{{ item.icon }}</span>
          <span v-show="!sidebarCollapsed" class="whitespace-nowrap">{{ item.label }}</span>
        </button>
      </nav>
    </aside>

    <!-- ===== 右侧主区域 ===== -->
    <div class="flex flex-col flex-1 min-w-0">
      <!-- 顶部栏 -->
      <header class="flex items-center justify-between h-14 px-5 bg-white border-b border-[#e5e7eb] shrink-0">
        <span class="text-sm text-[#6e6e73]">
          当前用户：<span class="text-[#1d1d1f] font-medium">{{ authStore.user?.username }}</span>
          <span class="text-[#aeaeb2]">（{{ authStore.user?.role }}）</span>
        </span>
        <button
          class="px-4 py-1.5 text-sm text-[#ff3b30] border border-[#ff3b30] rounded-lg hover:bg-red-50 transition-colors"
          @click="handleLogout"
        >退出登录</button>
      </header>

      <!-- 内容区 -->
      <main class="flex-1 min-h-0 overflow-hidden">
        <router-view />
      </main>
    </div>
  </div>
</template>