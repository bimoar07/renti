package com.example.renti.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

interface RentiApiService {
    @POST("api/v1/conversations")
    suspend fun createConversation(@Body request: ConversationCreateRequest): ConversationResponse

    @POST("api/v1/chat")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
}

object RetrofitClient {
    /**
     * Konfigurasi BASE_URL:
     * 1. Pengujian HP Fisik via USB (Rekomendasi Utama):
     *    - Jalankan: `adb reverse tcp:8000 tcp:8000`
     *    - Gunakan: "http://127.0.0.1:8000/"
     * 2. Pengujian Emulator Android Studio:
     *    - Gunakan: "http://10.0.2.2:8000/"
     * 3. Pengujian HP Fisik via Wi-Fi Lokal (tanpa kabel):
     *    - Gunakan IP LAN laptop, misal: "http://192.168.1.X:8000/"
     */
    private const val BASE_URL = "http://127.0.0.1:8000/"

    val apiService: RentiApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(RentiApiService::class.java)
    }
}