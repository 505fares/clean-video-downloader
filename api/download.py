import { Client } from "@gradio/client";

export default async function handler(req, res) {
    // التأكد من أن الطلب الموجه من نوع POST فقط
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { url } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'الرابط مطلوب' });
    }

    try {
        // 1. جلب بيانات ومسار الفيديو والصوت من API TikWM
        const tikwmResponse = await fetch('https://www.tikwm.com/api/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ url: url })
        });
        
        const tikwmData = await tikwmResponse.json();

        if (tikwmData.code !== 0) {
            return res.status(400).json({ error: 'فشل جلب الفيديو من تيك توك، تأكد من صحة الرابط.' });
        }

        const videoUrl = tikwmData.data.play;
        const musicUrl = tikwmData.data.music;

        // 2. الاتصال بسيرفر الذكاء الاصطناعي المجاني على Hugging Face لعزل الموسيقى
        let cleanAudioUrl = musicUrl; // في حال فشل العزل يستخدم الصوت الأصلي كاحتياط
        try {
            const client = await Client.connect("facebook/Music-Source-Separation");
            const result = await client.predict("/predict", [
                musicUrl,
                "HTDemucs"
            ]);
            
            if (result && result.data && result.data[0]) {
                cleanAudioUrl = result.data[0]; // رابط صوت الكلام بدون موسيقى
            }
        } catch (aiErr) {
            console.error("AI Separation Warning:", aiErr);
        }

        // 3. إرجاع النتيجة للواجهة (Index.html)
        return res.status(200).json({
            success: true,
            title: tikwmData.data.title || 'فيديو تيك توك',
            cover: tikwmData.data.cover,
            videoUrl: videoUrl,
            cleanAudioUrl: cleanAudioUrl
        });

    } catch (error) {
        console.error("Error:", error);
        return res.status(500).json({ error: 'حدث خطأ أثناء معالجة الطلب' });
    }
}
