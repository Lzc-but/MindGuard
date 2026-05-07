<script setup lang="ts">
import { ref } from "vue";
import { ElMessage, type UploadInstance, type UploadFile } from "element-plus";
import { rebuildKnowledgeIndex, uploadKnowledge } from "../../api/knowledge";

const uploadRef = ref<UploadInstance>();
const uploadLoading = ref(false);
const rebuildLoading = ref(false);

// 用于安全存储当前选中文件（解决拖拽/选择多场景一致性）
const currentFile = ref<File | null>(null);

// 文件变化时触发（拖拽 + 选择都生效）
const handleFileChange = (file: UploadFile) => {
  // 校验格式
  const name = file.name.toLowerCase();
  const allowTypes = [".txt", ".md", ".pdf"];
  const isValidType = allowTypes.some(type => name.endsWith(type));

  if (!isValidType) {
    ElMessage.error("仅支持 .txt / .md / .pdf 文件");
    uploadRef.value?.clearFiles();
    currentFile.value = null;
    return;
  }

  // 校验大小（示例：50MB）
  const maxSize = 50 * 1024 * 1024;
  if (file.size && file.size > maxSize) {
    ElMessage.error("文件不能超过 50MB");
    uploadRef.value?.clearFiles();
    currentFile.value = null;
    return;
  }

  // 安全赋值
  currentFile.value = file.raw ?? null;
};

// 上传
const doUpload = async () => {
  if (!currentFile.value) {
    ElMessage.warning("请先选择文件");
    return;
  }

  uploadLoading.value = true;
  try {
    const res = await uploadKnowledge(currentFile.value);
    ElMessage.success(`上传成功：${res.file}`);
  } catch (e: any) {
    const detail = e?.response?.data?.detail;
    ElMessage.error(detail || "上传失败，请重试");
  } finally {
    uploadLoading.value = false;
    // 安全清空
    if (uploadRef.value) {
      uploadRef.value.clearFiles();
    }
    currentFile.value = null;
  }
};

// 重建索引
const doRebuild = async () => {
  rebuildLoading.value = true;
  try {
    const res = await rebuildKnowledgeIndex();
    ElMessage.success(`重建完成，chunks=${res.chunks}`);
  } catch (e: any) {
    ElMessage.error("重建索引失败，请重试");
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
        ref="uploadRef"
        drag
        action=""
        :auto-upload="false"
        :show-file-list="true"
        :on-change="handleFileChange"
        :limit="1"
      >
        <div style="padding: 20px">拖拽文件到这里，或点击上传（仅 .txt / .md / .pdf）</div>
      </el-upload>

      <el-space>
        <el-button type="primary" :loading="uploadLoading" @click="doUpload">
          上传并增量建索引
        </el-button>
        <el-button type="warning" :loading="rebuildLoading" @click="doRebuild">
          全量重建索引
        </el-button>
      </el-space>
    </el-space>
  </el-card>
</template>