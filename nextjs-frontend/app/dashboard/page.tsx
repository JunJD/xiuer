import { Button } from "@/components/ui/button";
import Link from "next/link";
import { fetchNotes, fetchNotesStats } from "@/components/actions/notes-action";
import { XhsNoteResponse, NoteStatsResponse } from "../openapi-client";
import NotesDataTable from "@/components/NotesDataTable";

export default async function DashboardPage() {
  // 获取notes数据和统计信息
  const [notesData, statsData] = await Promise.all([
    fetchNotes() as Promise<XhsNoteResponse[]>,
    fetchNotesStats() as Promise<NoteStatsResponse>
  ]);

  const notes = Array.isArray(notesData) ? notesData : [];
  const stats = statsData || { total_notes: 0, new_notes: 0, changed_notes: 0, important_notes: 0, today_crawled: 0 };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">小红书笔记数据分析</h2>
      <p className="text-lg mb-6">
        在这里，您可以查看和分析爬取到的小红书笔记数据。
      </p>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">总笔记数</h3>
          <p className="text-2xl font-bold text-blue-600">{stats.total_notes}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">新笔记</h3>
          <p className="text-2xl font-bold text-green-600">{stats.new_notes}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">变更笔记</h3>
          <p className="text-2xl font-bold text-orange-600">{stats.changed_notes}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">重要笔记</h3>
          <p className="text-2xl font-bold text-red-600">{stats.important_notes}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">今日爬取</h3>
          <p className="text-2xl font-bold text-purple-600">{stats.today_crawled}</p>
        </div>
      </div>

      <div className="mb-6 flex gap-4">
        <Link href="/keywords">
          <Button variant="outline" className="text-lg px-4 py-2">
            管理关键词
          </Button>
        </Link>
        <Link href="/dashboard/search-notes">
          <Button variant="outline" className="text-lg px-4 py-2">
            搜索笔记
          </Button>
        </Link>
      </div>

      <section className="p-6 bg-white rounded-lg shadow-lg mt-8">
        <h2 className="text-xl font-semibold mb-4">最新笔记数据</h2>
        <NotesDataTable notes={notes} />
      </section>
    </div>
  );
}
