<script setup lang="ts">
import { computed, ref } from "vue";
import { analyzeMental, type MentalResponse } from "../../api/mental";

const userId = ref("u-001");
const text = ref("");
const loading = ref(false);
const result = ref<MentalResponse | null>(null);

const tagType = computed(() => {
  if (!result.value) return "info";
  if (result.value.status === "high_risk") return "danger";
  if (result.value.status === "medium_risk") return "warning";
  return "success";
});

const submit = async () => {
  if (!text.value.trim()) return;
  loading.value = true;
  try {
    result.value = await analyzeMental({
      user_id: userId.value,
      text: text.value,
    });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <h2 class="page-title">心理状态分析</h2>
  <el-card>
    <el-form label-position="top">
      <el-form-item label="用户ID">
        <el-input v-model="userId" />
      </el-form-item>
      <el-form-item label="待分析文本">
        <el-input v-model="text" type="textarea" :rows="5" placeholder="请输入用户当前情绪或聊天内容" />
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="submit">开始分析</el-button>
    </el-form>
  </el-card>

  <el-card v-if="result" style="margin-top: 16px">
    <el-space direction="vertical" alignment="start">
      <el-tag :type="tagType">{{ result.status }}</el-tag>
      <div>风险评分：{{ result.score }}</div>
      <div>建议：{{ result.suggestion }}</div>
      <el-alert
        v-if="result.status === 'high_risk'"
        title="检测到高风险，请立刻联系紧急援助或心理中心。"
        type="error"
        :closable="false"
      />
    </el-space>
  </el-card>
</template>
