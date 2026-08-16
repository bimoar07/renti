package com.example.renti.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

interface RentiApiService {
    @POST("api/v1/chat")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
}

object RetrofitClient {
    // Sesuaikan URL jika menguji via device fisik (gunakan IP lokal laptop Bimo, misal: http://192.168.1.x:8000/)
    // Jika via Emulator Android Studio, gunakan http://10.0.2.2:8000/
    private const val BASE_URL = "http://10.0.2.2:8000/"

    val apiService: RentiApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(RentiApiService::class.java)
    }
}