#include <windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <iostream>

#pragma comment(lib, "ole32.lib")

int main() {
    CoInitialize(nullptr);

    IMMDeviceEnumerator* pEnumerator = nullptr;
    IMMDevice* pDevice = nullptr;
    IAudioClient* pAudioClient = nullptr;

    CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr,
        CLSCTX_ALL, __uuidof(IMMDeviceEnumerator),
        (void**)&pEnumerator);

    pEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &pDevice);

    pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL,
        nullptr, (void**)&pAudioClient);

    WAVEFORMATEX* pwfx = nullptr;
    pAudioClient->GetMixFormat(&pwfx);

    pAudioClient->Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK,
        0, 0, pwfx, nullptr
    );

    IAudioCaptureClient* pCaptureClient = nullptr;
    pAudioClient->GetService(__uuidof(IAudioCaptureClient),
        (void**)&pCaptureClient);

    pAudioClient->Start();

    setvbuf(stdout, nullptr, _IONBF, 0);

    while (true) {
        UINT32 packetLength = 0;
        pCaptureClient->GetNextPacketSize(&packetLength);

        while (packetLength != 0) {
            BYTE* pData;
            UINT32 numFrames;
            DWORD flags;

            pCaptureClient->GetBuffer(&pData, &numFrames, &flags, nullptr, nullptr);

            float* samples = (float*)pData;

            for (UINT32 i = 0; i < numFrames; ++i)
                std::cout << samples[i] << "\n";

            pCaptureClient->ReleaseBuffer(numFrames);
            pCaptureClient->GetNextPacketSize(&packetLength);
        }
    }

    CoUninitialize();
    return 0;
}