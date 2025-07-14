import { fetchNotes } from "@/components/actions/notes-action";
import { XhsNoteResponse } from "@/app/openapi-client";
import ExpandableNoteGrid from "../_components/flow-list";

export default async function MobileNotesPage() {
  const notesData = await fetchNotes() as XhsNoteResponse[];
  const notes = Array.isArray(notesData) ? notesData : [];

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