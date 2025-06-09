import React from 'react';
import {useSortable} from '@dnd-kit/sortable';
import {CSS} from '@dnd-kit/utilities';
import { MenuIcon } from 'lucide-react';

interface SortableItemProps {
    id: string;
    title: string;
}

export function SortableItem({ id, title }: SortableItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({id: id});
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  
  return (
    <li ref={setNodeRef} style={style} {...attributes} {...listeners} className="flex items-center bg-white p-2 rounded-md shadow-sm text-sm">
        <MenuIcon className="h-4 w-4 mr-2 text-gray-400 cursor-grab" />
        <span className="flex-grow text-gray-800">{title}</span>
    </li>
  );
} 