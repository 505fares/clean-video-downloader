export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    let { url } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'الرابط مطلوب' });
    }

    // تنظيف الرابط لو ينتهي بشرطة أو رموز زائدة بالبداية
    url = url.trim().replace(/^\/+/, '');

    try {
        // 1. جلب الفيديو من TikWM
        const tikwmResponse = await fetch('https://www.tikwm.com/api/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ url: url })
        });
        
        const tikwmData = await tikwmResponse.json();

        if (tikwmData.code !== 0) {
            return res.status(400).json({ error: 'فشل جلب الفيديو، تأكد من صحة رابط التيك توك.' });
        }

        const videoUrl = tikwmData.data.play;
        const musicUrl = tikwmData.data.music;

        // إرجاع النتيجة فوراً لتجنب انتهاء وقت سيرفر Vercel (Timeout)
        return res.status(200).json({
            success: true,
            title: tikwmData.data.title || 'فيديو تيك توك',
            cover: tikwmData.data.cover,
            videoUrl: videoUrl,
            cleanAudioUrl: musicUrl
        });

    } catch (error) {
        console.error("Error:", error);
        return res.status(500).json({ error: 'حدث خطأ في السيرفر' });
    }
}
