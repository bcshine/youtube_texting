import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from youtube_text_extractor import YouTubeTextExtractor


class YouTubeExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("유튜브 텍스트 추출 프로그램")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 추출기 초기화
        self.extractor = YouTubeTextExtractor()
        
        # UI 생성
        self.create_widgets()
        
    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="유튜브 텍스트 추출 프로그램", 
                               font=("맑은 고딕", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL 입력 섹션
        url_frame = ttk.LabelFrame(main_frame, text="유튜브 URL", padding="10")
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.extract_button = ttk.Button(url_frame, text="추출 시작", 
                                        command=self.start_extraction)
        self.extract_button.grid(row=1, column=1)
        
        # 진행 상황 섹션
        progress_frame = ttk.LabelFrame(main_frame, text="진행 상황", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_var = tk.StringVar(value="대기 중...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 결과 섹션
        result_frame = ttk.LabelFrame(main_frame, text="추출 결과", padding="10")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # 텍스트 출력 영역
        self.result_text = tk.Text(result_frame, height=15, width=70, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 버튼 섹션
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="HTML 파일 저장", 
                                     command=self.save_html, state='disabled')
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="결과 지우기", 
                                      command=self.clear_results)
        self.clear_button.grid(row=0, column=1)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        url_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
    def update_progress(self, message):
        """진행 상황 업데이트"""
        self.progress_var.set(message)
        self.root.update_idletasks()
        
    def start_extraction(self):
        """추출 시작 (별도 스레드에서 실행)"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "유튜브 URL을 입력해주세요.")
            return
        
        # UI 상태 변경
        self.extract_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.progress_bar.start()
        self.result_text.delete(1.0, tk.END)
        
        # 별도 스레드에서 추출 실행
        thread = threading.Thread(target=self.extract_text, args=(url,))
        thread.daemon = True
        thread.start()
        
    def extract_text(self, url):
        """텍스트 추출 실행"""
        try:
            self.update_progress("URL 분석 중...")
            
            # 비디오 ID 추출
            video_id = self.extractor.extract_video_id(url)
            if not video_id:
                self.show_error("올바른 유튜브 URL이 아닙니다.")
                return
            
            self.update_progress("비디오 정보 가져오는 중...")
            self.extractor.get_video_info(video_id)
            
            # 비디오 정보를 결과창에 미리 표시
            video_info = self.extractor.video_info
            info_preview = f"📺 {video_info.get('title', '제목 없음')}\n"
            info_preview += f"🎬 {video_info.get('channel', '정보 없음')}\n"
            info_preview += f"🆔 {video_info.get('video_id', '')}\n\n"
            info_preview += "텍스트 추출 중...\n"
            
            def update_preview():
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, info_preview)
            self.root.after(0, update_preview)
            
            self.update_progress("자막 확인 중...")
            transcript_success = self.extractor.extract_transcript(video_id)
            
            # 자막이 없으면 음성 인식 시도
            if not transcript_success:
                self.update_progress("자막이 없습니다. 음성 인식을 시작합니다...")
                
                # 음성 인식 안내 메시지 추가
                speech_info = info_preview + "자막이 없어 음성 인식을 시작합니다.\n"
                speech_info += "⏱️ 이 과정은 비디오 길이에 따라 1-10분 소요될 수 있습니다.\n"
                speech_info += "🧠 AI가 음성을 분석하고 텍스트로 변환 중...\n\n"
                speech_info += "잠시만 기다려주세요! ☕"
                
                def update_speech_info():
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, speech_info)
                self.root.after(0, update_speech_info)
                
                # 진행률 바를 더 부드럽게
                self.progress_bar.configure(mode='indeterminate')
                
                if not self.extractor.extract_audio_and_transcribe(video_id):
                    # 더 자세한 에러 메시지 제공
                    error_msg = "자막 추출과 음성 인식 모두 실패했습니다.\n\n"
                    error_msg += "가능한 원인:\n"
                    error_msg += "• 이 비디오에 자막이 없고 음성도 명확하지 않습니다\n"
                    error_msg += "• 비디오가 비공개이거나 제한되어 있습니다\n"
                    error_msg += "• FFmpeg가 설치되지 않았습니다\n"
                    error_msg += "• Whisper가 설치되지 않았습니다\n\n"
                    error_msg += "해결 방법:\n"
                    error_msg += "1. 자막이 있는 비디오를 시도해보세요\n"
                    error_msg += "2. pip install openai-whisper 명령어로 Whisper를 설치하세요\n"
                    error_msg += "3. FFmpeg를 설치하세요 (https://ffmpeg.org/download.html)\n\n"
                    error_msg += "예시 비디오: https://www.youtube.com/watch?v=jNQXAC9IVRw"
                    self.show_error(error_msg)
                    return
                else:
                    # 음성 인식 성공 안내
                    success_info = info_preview + "🎉 음성 인식 성공!\n"
                    success_info += f"📝 {len(self.extractor.transcript_data)}개 구간의 텍스트를 추출했습니다.\n\n"
                    success_info += "텍스트 포맷팅 중..."
                    
                    def update_success_info():
                        self.result_text.delete(1.0, tk.END)
                        self.result_text.insert(tk.END, success_info)
                    self.root.after(0, update_success_info)
            
            self.update_progress("텍스트 포맷팅 중...")
            formatted_text = self.extractor.format_transcript()
            
            # 결과 표시
            self.show_results(formatted_text)
            
            self.update_progress("완료!")
            
            # 성공 메시지도 더 상세하게
            if transcript_success:
                success_msg = "✅ 자막에서 텍스트 추출 완료!"
            else:
                success_msg = "🎤 음성 인식으로 텍스트 추출 완료!"
            success_msg += f"\n📊 총 {len(self.extractor.transcript_data)}개 구간 추출됨"
            success_msg += "\n💾 HTML 파일 저장 준비 완료"
            
            messagebox.showinfo("추출 완료", success_msg)
            
        except Exception as e:
            self.show_error(f"오류 발생: {str(e)}")
        finally:
            # UI 상태 복원
            self.extract_button.config(state='normal')
            self.progress_bar.stop()
            
    def show_results(self, text):
        """결과 텍스트 표시"""
        def update_ui():
            self.result_text.delete(1.0, tk.END)
            
            # 비디오 정보 표시
            video_info = self.extractor.video_info
            info_text = f"제목: {video_info.get('title', '정보 없음')}\n"
            info_text += f"채널: {video_info.get('channel', '정보 없음')}\n"
            info_text += f"비디오 ID: {video_info.get('video_id', '')}\n"
            info_text += f"자막 항목 수: {len(self.extractor.transcript_data)}개\n"
            info_text += "=" * 50 + "\n\n"
            
            self.result_text.insert(tk.END, info_text)
            self.result_text.insert(tk.END, text)
            
            # 저장 버튼 활성화
            self.save_button.config(state='normal')
        
        self.root.after(0, update_ui)
        
    def show_error(self, message):
        """에러 메시지 표시"""
        def show_msg():
            messagebox.showerror("오류", message)
            self.extract_button.config(state='normal')
            self.progress_bar.stop()
            self.update_progress("대기 중...")
        
        self.root.after(0, show_msg)
        
    def save_html(self):
        """HTML 파일 저장"""
        if not self.extractor.formatted_text:
            messagebox.showwarning("경고", "저장할 내용이 없습니다.")
            return
        
        # 파일 이름 제안
        video_title = self.extractor.video_info.get('title', 'youtube_transcript')
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        default_filename = f"{safe_title[:30]}_{self.extractor.video_info.get('video_id', '')}.html"
        
        # 파일 저장 대화상자
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialvalue=default_filename
        )
        
        if filename:
            try:
                saved_file = self.extractor.save_to_html(filename)
                messagebox.showinfo("저장 완료", f"HTML 파일이 저장되었습니다:\n{saved_file}")
                
                # 파일 열기 여부 확인
                if messagebox.askyesno("파일 열기", "저장된 HTML 파일을 브라우저에서 열까요?"):
                    os.startfile(saved_file)  # Windows용
                    
            except Exception as e:
                messagebox.showerror("저장 오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")
                
    def clear_results(self):
        """결과 지우기"""
        self.result_text.delete(1.0, tk.END)
        self.save_button.config(state='disabled')
        self.progress_var.set("대기 중...")
        self.url_var.set("")


def main():
    root = tk.Tk()
    app = YouTubeExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 