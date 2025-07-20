import { fetchNotes } from "@/components/actions/notes-action";
import { XhsNoteResponse } from "@/app/openapi-client";
import type { NotesListResponse } from "@/app/openapi-client/types.gen";
import ExpandableNoteGrid from "../_components/flow-list";

export default async function MobileNotesPage() {
  const notesData = await fetchNotes({
    is_new: true,
    is_changed: true,
    is_important: true,
    today_only: true,
  });
  
  // 现在需要从 NotesListResponse 中提取 notes 数组
  let notes: XhsNoteResponse[] = [];
  if (notesData && typeof notesData === 'object' && 'notes' in notesData) {
    notes = (notesData as NotesListResponse).notes;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 p-4 z-20">
        <h1 className="text-xl font-bold text-center">小红书笔记</h1>
        <p className="text-sm text-gray-600 text-center mt-1">
          共 {notes.length} 条笔记
        </p>
      </div>
      
      <ExpandableNoteGrid notes={notes} />
    </div>
  );
} 