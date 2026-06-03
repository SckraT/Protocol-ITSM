// API для работы с совещаниями.
import { apiDelete, apiGet, apiPatch, apiPost } from './client';
import type { Meeting, MeetingCreatePayload, MeetingUpdatePayload, PaginatedResponse } from './types';

/** Получить список совещаний. */
export async function fetchMeetings(search?: string): Promise<PaginatedResponse<Meeting>> {
  const qs = new URLSearchParams({ page_size: '1000' });
  if (search) qs.set('search', search);
  return apiGet<PaginatedResponse<Meeting>>(`/meetings?${qs.toString()}`);
}

/** Получить одно совещание по ID. */
export async function fetchMeeting(id: number): Promise<Meeting> {
  return apiGet<Meeting>(`/meetings/${id}`);
}

/** Создать совещание. */
export async function createMeeting(data: MeetingCreatePayload): Promise<Meeting> {
  return apiPost<Meeting>('/meetings', data);
}

/** Частично обновить совещание. */
export async function updateMeeting(id: number, data: MeetingUpdatePayload): Promise<Meeting> {
  return apiPatch<Meeting>(`/meetings/${id}`, data);
}

/** Удалить совещание. */
export async function deleteMeeting(id: number): Promise<void> {
  return apiDelete(`/meetings/${id}`);
}
