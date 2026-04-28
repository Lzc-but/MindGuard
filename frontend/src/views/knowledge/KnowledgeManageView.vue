<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { rebuildKnowledgeIndex, uploadKnowledge } from "../../api/knowledge";

const fileList = ref<File[]>([]);
const uploadLoading = ref(false);
const rebuildLoading = ref(false);

const beforeUpload = (rawFile: File) => {
  const name = rawFile.name.toLowerCase();
  if (!name.endsWith(".txt") && !name.endsWith(".md")) {
    ElMessage.error("仅支持 .txt 或 .md 文件");
    return false;
  }
  fileList.value = [rawFile];
  return false;
};

const doUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.warning("请先选择文件");
    return;
  }
  uploadLoading.value = true;
  try {
    const res = await uploadKnowledge(fileList.value[0]);
    ElMessage.success(`上传成功：${res.file}`);
    fileList.value = [];
  } finally {
    uploadLoading.value = false;
  }
};

const doRebuild = async () => {
  rebuildLoading.value = true;
  try {
    const res = await rebuildKnowledgeIndex();
    ElMessage.success(`重建完成，chunks=${res.chunks}`);
  } finally {
    rebuildLoading.value = false;
  }
};
</script>

<template>
  <h2 class="page-title">知识库管理（管理员）</h2>
  <el-card>
    <el-space direction="vertical" alignment="start" style="width: 100%">
      <el-upload
        drag
        action="#"
        :auto-upload="false"
        :show-file-list="true"
        :before-upload="beforeUpload"
        :limit="1"
      >
        <div style="padding: 20px">拖拽文件到这里，或点击上传（仅 .txt/.md）</div>
      </el-upload>
      <el-space>
        <el-button type="primary" :loading="uploadLoading" @click="doUpload">上传并增量建索引</el-button>
        <el-button type="warning" :loading="rebuildLoading" @click="doRebuild">全量重建索引</el-button>
      </el-space>
    </el-space>
  </el-card>
</template>
