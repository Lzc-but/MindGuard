import { defineStore } from "pinia";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  createConversation,
  deleteConversation,
  listConversationMessages,
  listConversations,
  renameConversation,
  sendConversationMessage,
  type ChatResponse,
  type ConversationItem,
  type ConversationMessage,
} from "../api/chat";

export interface UiMessageItem {
  role: "user" | "assistant";
  content: string;
  created_at?: string;
  references?: string[];
}

export const useChatStore = defineStore("chat", {
  state: () => ({
    convoLoading: false,
    loading: false,
    conversations: [] as ConversationItem[],
    currentConversationId: "",
    messages: [] as UiMessageItem[],
  }),
  actions: {
    async refreshConversations() {
      this.convoLoading = true;
      try {
        this.conversations = await listConversations();
      } finally {
        this.convoLoading = false;
      }
    },

    async selectConversation(conversationId: string) {
      this.currentConversationId = conversationId;
      const rows: ConversationMessage[] = await listConversationMessages(conversationId);
      this.messages = rows.map((item) => ({
        role: item.role,
        content: item.content,
        created_at: item.created_at,
      }));
    },

    async createNewConversation() {
      const created = await createConversation();
      await this.refreshConversations();
      await this.selectConversation(created.id);
      return created;
    },

    async removeConversation(conversationId: string) {
      await deleteConversation(conversationId);
      ElMessage.success("会话已删除");
      await this.refreshConversations();

      if (this.currentConversationId === conversationId) {
        const first = this.conversations[0];
        if (first) {
          await this.selectConversation(first.id);
        } else {
          this.currentConversationId = "";
          this.messages = [];
        }
      }
    },

    async promptRenameConversation(item: ConversationItem) {
      try {
        const { value } = await ElMessageBox.prompt("请输入新的会话名称", "重命名会话", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          inputValue: item.title,
          inputValidator: (val: string) => {
            const text = val.trim();
            if (!text) return "会话名称不能为空";
            if (text.length > 50) return "会话名称最多 50 个字符";
            return true;
          },
        });
        await renameConversation(item.id, value.trim());
        ElMessage.success("重命名成功");
        await this.refreshConversations();
      } catch {
        // 用户取消或请求失败都在此分支，无需额外提示
      }
    },

    async sendMessage(question: string) {
      const text = question.trim();
      if (!text) return null;

      if (!this.currentConversationId) {
        await this.createNewConversation();
      }

      this.messages.push({ role: "user", content: text });
      this.loading = true;
      try {
        const res: ChatResponse = await sendConversationMessage(this.currentConversationId, text);
        this.messages.push({
          role: "assistant",
          content: res.answer,
          references: res.references,
        });
        return res;
      } catch {
        ElMessage.error("消息发送失败");
        return null;
      } finally {
        this.loading = false;
      }
    },
  },
});

