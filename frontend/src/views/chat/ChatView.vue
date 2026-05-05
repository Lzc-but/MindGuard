<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { useChatStore } from "../../stores/chat";

const question = ref("");
const chatStore = useChatStore();
const messagesContainer = ref<HTMLElement | null>(null);
const showCopyButton = ref(false);

const sendMessage = async () => {
  const text = question.value.trim();
  if (!text) return;
  question.value = "";
  await chatStore.sendMessage(text);
  await nextTick();
  scrollToBottom();
};

const copyMessage = async (content: string) => {
  const text = content.trim();
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success("已复制");
  } catch {
    ElMessage.error("复制失败，请手动复制");
  }
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 消息变化时自动滚动到底部
watch(
  () => chatStore.messages.length,
  () => nextTick(scrollToBottom)
);

onMounted(async () => {
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
  await nextTick();
  scrollToBottom();
});
</script>

<template>
  <div class="flex flex-col h-full bg-white">
    <!-- 标题栏 -->
    <div class="flex items-center justify-center h-12 px-4 border-b border-[#f0f0f0] shrink-0">
      <span class="text-sm font-medium text-[#6e6e73]">心理健康助手</span>
    </div>

    <!-- 消息列表 -->
    <div
      ref="messagesContainer"
      class="flex-1 min-h-0 overflow-y-auto px-4 py-5 space-y-5 scroll-smooth"
    >
      <!-- 空状态 -->
      <div
        v-if="chatStore.messages.length === 0"
        class="flex flex-col items-center justify-center h-full text-center gap-2"
      >
        <span class="text-4xl">🧘</span>
        <p class="text-lg font-semibold text-[#1d1d1f]">今天想聊些什么？</p>
        <p class="text-sm text-[#aeaeb2] max-w-xs">
          可以输入你的情绪状态、困惑或压力来源，我会结合知识库帮助你。
        </p>
      </div>

      <!-- 消息列表 -->
      <template v-for="(item, idx) in chatStore.messages" :key="idx">
        <!-- 用户消息 -->
        <div v-if="item.role === 'user'" class="flex justify-end">
          <div class="max-w-[75%] px-4 py-2.5 rounded-2xl rounded-br-md text-sm text-white bg-[#4f6ef7] leading-relaxed whitespace-pre-wrap break-words">
            {{ item.content }}
          </div>
        </div>

        <!-- AI 消息 -->
        <div v-else class="flex gap-3">
          <!-- AI 头像 -->
          <div class="flex items-center justify-center w-8 h-8 rounded-full bg-[#eef1ff] text-[#4f6ef7] text-sm shrink-0 mt-0.5">
            AI
          </div>
          <div class="flex flex-col gap-1.5 max-w-[75%] min-w-0">
            <!-- 消息气泡 -->
            <div class="px-4 py-2.5 rounded-2xl rounded-bl-md text-sm text-[#1d1d1f] bg-[#f5f5f7] leading-relaxed whitespace-pre-wrap break-words">
              {{ item.content }}
              <!-- 加载动画 -->
              <span
                v-if="chatStore.loading && idx === chatStore.messages.length - 1 && !item.content"
                class="inline-flex gap-0.5 ml-1"
              >
                <span class="w-1.5 h-1.5 bg-[#aeaeb2] rounded-full animate-bounce" style="animation-delay:0s"></span>
                <span class="w-1.5 h-1.5 bg-[#aeaeb2] rounded-full animate-bounce" style="animation-delay:0.15s"></span>
                <span class="w-1.5 h-1.5 bg-[#aeaeb2] rounded-full animate-bounce" style="animation-delay:0.3s"></span>
              </span>
            </div>
            <!-- 复制按钮 - 有内容时显示 -->
            <div v-if="item.content" class="flex items-center gap-2">
              <button
                class="flex items-center gap-1 px-2 py-1 text-xs text-[#8e8e93] hover:text-[#4f6ef7] hover:bg-[#f5f5f7] rounded-lg transition-colors"
                @click="copyMessage(item.content)"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                复制
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 底部输入区 -->
    <div class="shrink-0 px-4 pb-4 pt-2">
      <div class="relative max-w-3xl mx-auto">
        <!-- 输入框容器 -->
        <div
          class="relative flex items-end gap-2 bg-[#f5f5f7] rounded-2xl border border-transparent focus-within:border-[#d1d1d6] focus-within:bg-white transition-all px-4 py-2.5"
          @mouseenter="showCopyButton = true"
          @mouseleave="showCopyButton = false"
        >
          <textarea
            v-model="question"
            :rows="1"
            class="flex-1 resize-none bg-transparent outline-none text-sm text-[#1d1d1f] placeholder-[#aeaeb2] leading-relaxed max-h-[160px] py-0.5"
            placeholder="输入内容，Enter 发送，Shift+Enter 换行"
            @input="(e: Event) => { const t = e.target as HTMLTextAreaElement; t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight, 160) + 'px'; }"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <!-- 悬浮复制图标 - 鼠标悬浮输入区域时显示 -->
          <button
            v-show="showCopyButton"
            class="flex items-center justify-center w-8 h-8 rounded-lg text-[#8e8e93] hover:text-[#4f6ef7] hover:bg-[#eef1ff] transition-all shrink-0"
            title="复制最后一条回复"
            @click="copyMessage(chatStore.messages.filter(m => m.role === 'assistant').slice(-1)[0]?.content || '')"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
          <!-- 发送按钮 -->
          <button
            class="flex items-center justify-center w-8 h-8 rounded-lg transition-all shrink-0"
            :class="question.trim()
              ? 'bg-[#4f6ef7] text-white hover:bg-[#3d5ce5]'
              : 'text-[#aeaeb2] cursor-default'"
            :disabled="!question.trim()"
            @click="sendMessage"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>