<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { useChatStore } from "../../stores/chat";

const question = ref("");
const chatStore = useChatStore();

const sendMessage = async () => {
  const text = question.value.trim();
  if (!text) return;
  question.value = "";
  await chatStore.sendMessage(text);
};

const copyMessage = async (content: string) => {
  const text = content.trim();
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success("已复制消息");
  } catch {
    ElMessage.error("复制失败，请手动复制");
  }
};

onMounted(async () => {
  // 会话列表由左侧导航管理；这里兜底确保进入聊天页时有可用会话
  if (!chatStore.conversations.length) {
    await chatStore.refreshConversations();
  }
  if (!chatStore.conversations.length) {
    await chatStore.createNewConversation();
    return;
  }
  if (!chatStore.currentConversationId) {
    await chatStore.selectConversation(chatStore.conversations[0].id);
  }
});
</script>

<template>
  <div class="chat-page">
    <div class="chat-main">
      <div class="chat-title">心理健康助手</div>
      <el-scrollbar class="message-scroll">
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <p>今天想聊些什么？</p>
          <span>可以输入你的情绪状态、困惑或压力来源，我会结合知识库帮助你。</span>
        </div>
        <div
          v-for="(item, idx) in chatStore.messages"
          :key="idx"
          class="message-row"
          :class="item.role === 'user' ? 'user-row' : 'ai-row'"
        >
          <div class="message-meta">{{ item.role === "user" ? "你" : "AI 助手" }}</div>
          <div class="message-bubble">
            <div class="message-content">{{ item.content }}</div>
            <div class="message-bottom">
              <div v-if="item.references?.length" class="message-ref">
                引用：{{ item.references.join(" | ") }}
              </div>
              <el-button text size="small" @click="copyMessage(item.content)">复制</el-button>
            </div>
          </div>
        </div>
      </el-scrollbar>

      <div class="chat-input-wrap">
        <el-input
          v-model="question"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          placeholder="输入内容，Ctrl + Enter 发送"
          @keydown.enter.ctrl.prevent="sendMessage"
        />
        <div class="input-actions">
          <span class="hint-text">支持多轮上下文，建议描述更具体</span>
          <el-button type="primary" :loading="chatStore.loading" @click="sendMessage">发送</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  height: calc(100vh - 136px);
}

.chat-main {
  background: #ffffff;
  border: 1px solid #e9eef5;
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100%;
}

.chat-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
}

.message-scroll {
  flex: 1;
  min-height: 0;
  padding-right: 6px;
}

.empty-state {
  height: 100%;
  display: grid;
  place-content: center;
  text-align: center;
  color: #8592a6;
  gap: 6px;
}

.empty-state p {
  margin: 0;
  color: #4e5969;
  font-size: 18px;
  font-weight: 600;
}

.message-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 14px;
}

.user-row {
  align-items: flex-end;
}

.ai-row {
  align-items: flex-start;
}

.message-meta {
  font-size: 12px;
  color: #8a94a6;
  margin-bottom: 4px;
}

.message-bubble {
  max-width: min(78%, 760px);
  border-radius: 14px;
  padding: 10px 12px;
  white-space: pre-wrap;
  transition: transform 0.2s ease;
}

.message-bubble:hover {
  transform: translateY(-1px);
}

.user-row .message-bubble {
  background: linear-gradient(135deg, #5b9dff, #3e82f6);
  color: #fff;
}

.ai-row .message-bubble {
  background: #f3f7fd;
  color: #2d3a4f;
}

.message-content {
  line-height: 1.7;
}

.message-bottom {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.message-ref {
  font-size: 12px;
  opacity: 0.85;
}

.chat-input-wrap {
  margin-top: 14px;
  border: 1px solid #e2e9f5;
  background: #f8fbff;
  border-radius: 14px;
  padding: 10px;
}

.input-actions {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint-text {
  font-size: 12px;
  color: #93a1b6;
}
</style>
