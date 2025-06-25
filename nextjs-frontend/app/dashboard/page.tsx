import { Button } from "@/components/ui/button";
import Link from "next/link";
import { fetchKeywords, removeKeyword, toggleKeyword } from "@/components/actions/keywords-action";
import { KeywordListResponse, KeywordResponse } from "../openapi-client";
import EasyTable, { ColumnDefinition } from "@/components/EasyTable";

export default async function DashboardPage() {
  const { keywords } = (await fetchKeywords()) as KeywordListResponse;

  const handleDelete = async (row: KeywordResponse) => {
    await removeKeyword(row.id);
  };

  const handleToggle = async (row: KeywordResponse) => {
    await toggleKeyword(row.id);
  };

  const columns: ColumnDefinition<KeywordResponse>[] = [
    {
      key: "keyword",
      title: "关键词",
      width: "120px",
    },
    {
      key: "category",
      title: "分类",
      render: (value) => (value as string) || "无分类",
    },
    {
      key: "weight",
      title: "权重",
      align: "center",
    },
    {
      key: "is_active",
      title: "状态",
      align: "center",
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
        }`}>
          {value ? "启用" : "禁用"}
        </span>
      ),
    },
    {
      key: "created_at",
      title: "创建时间",
      render: (value) => new Date(value as string).toLocaleDateString(),
    },
    {
      key: "id",
      title: "操作",
      align: "center",
      actions: [
        {
          label: "编辑",
          onClick: (row) => {
            // TODO: 实现编辑功能
            console.log("编辑", row);
          },
        },
        {
          label: "切换状态",
          onClick: (row) => {
            handleToggle(row);
          },
        },
        {
          label: "删除",
          onClick: (row) => {
            handleDelete(row);
          },
          variant: "destructive",
        },
      ],
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">欢迎来到您的控制台</h2>
      <p className="text-lg mb-6">
        在这里，您可以查看关键词概览并管理它们。
      </p>

      <div className="mb-6">
        <Link href="/dashboard/add-keyword">
          <Button variant="outline" className="text-lg px-4 py-2">
            添加新关键词
          </Button>
        </Link>
      </div>

      <section className="p-6 bg-white rounded-lg shadow-lg mt-8">
        <h2 className="text-xl font-semibold mb-4">关键词</h2>
        <EasyTable 
          columns={columns} 
          data={keywords} 
          emptyMessage="暂无关键词数据。"
        />
      </section>
    </div>
  );
}
