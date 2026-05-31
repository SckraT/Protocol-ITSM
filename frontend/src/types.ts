export interface Department {
  id: number;
  name: string;
}

export interface Executor {
  id: number;
  name: string;
  department_id: number | null;
  department_name: string | null;
}

export interface Status {
  id: number;
  item_id: number;
  status_date: string | null;
  status_note: string | null;
  created_at: string;
}

export interface Item {
  id: number;
  topic: string;
  ticket: string | null;
  priority: 'high' | 'medium' | 'low' | null;
  state: 'in_progress' | 'postponed' | 'closed';
  due_date: string | null;
  created_at: string;
  executors: Executor[];
  recent_statuses: Status[];
  status_count: number;
}

export type Theme = 'light' | 'dark';
export type SortDir = 'asc' | 'desc';
export type ItemState = Item['state'];
export type Priority = NonNullable<Item['priority']>;
