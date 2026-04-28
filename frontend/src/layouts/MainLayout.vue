<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import { useChatStore } from "../stores/chat";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const chatStore = useChatStore();

const activeMenu = computed(() => route.path);
const isChatRoute = computed(() => route.path.startsWith("/chat"));

const menuItems = computed(() => {
  const items = [
    { index: "/chat", label: "AI 聊天" },
    { index: "/mental/analyze", label: "心理分析" },
    { index: "/profile", label: "个人信息" },
  ];
  if (authStore.isAdmin) {
    items.splice(2, 0, { index: "/knowledge/manage", label: "知识库管理" });
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
  <el-container class="layout-root">
    <el-aside width="220px" class="layout-aside">
      <div class="layout-logo">心护AI</div>

      <div v-if="isChatRoute" class="chat-nav">
        <button class="chat-nav-new" type="button" @click="goChatAndCreate">+ 新对话</button>
        <el-scrollbar class="chat-nav-scroll" v-loading="chatStore.convoLoading">
          <div
            v-for="item in chatStore.conversations"
            :key="item.id"
            class="chat-nav-item"
            :class="{ active: item.id === chatStore.currentConversationId }"
            @click="selectConversation(item.id)"
          >
            <div class="chat-nav-title">{{ item.title }}</div>
            <div class="chat-nav-actions">
              <el-button type="primary" text size="small" @click.stop="chatStore.promptRenameConversation(item)">
                重命名
              </el-button>
              <el-button type="danger" text size="small" @click.stop="chatStore.removeConversation(item.id)">
                删除
              </el-button>
            </div>
          </div>
        </el-scrollbar>
        <div class="chat-nav-divider" />
      </div>

      <el-menu :default-active="activeMenu" class="layout-menu" @select="handleSelect">
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          {{ item.label }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="layout-user">当前用户：{{ authStore.user?.username }}（{{ authStore.user?.role }}）</div>
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-root {
  min-height: 100vh;
}

.layout-aside {
  background: #f7faff;
  border-right: 1px solid #e8eef8;
  display: flex;
  flex-direction: column;
}

.layout-logo {
  padding: 20px;
  font-size: 20px;
  font-weight: 700;
  color: #3a7ce7;
}

.chat-nav {
  padding: 0 12px 12px;
}

.chat-nav-new {
  width: 100%;
  border: 1px solid #d9e7ff;
  background: linear-gradient(135deg, #5b9dff, #3e82f6);
  color: #fff;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.chat-nav-new:hover {
  transform: translateY(-1px);
}

.chat-nav-scroll {
  margin-top: 12px;
  height: calc(100vh - 360px);
}

.chat-nav-item {
  background: #ffffff;
  border: 1px solid #eaf0f6;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-nav-item:hover {
  border-color: #b4cdf8;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.08);
}

.chat-nav-item.active {
  background: #edf4ff;
  border-color: #84b1ff;
}

.chat-nav-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-nav-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
}

.chat-nav-divider {
  height: 1px;
  background: #e8eef8;
  margin-top: 10px;
}

.layout-menu {
  border-right: none;
  background: transparent;
}

.layout-header {
  background: #ffffff;
  border-bottom: 1px solid #e9eef6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.layout-user {
  color: #4e5d74;
}

.layout-main {
  padding: 16px;
}
</style>
