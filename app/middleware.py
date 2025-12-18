from django.utils.deprecation import MiddlewareMixin
from .models import AffiliateReferral, AffiliateProfile

class AffiliateTrackingMiddleware(MiddlewareMixin):
    """Track affiliate referrals via URL parameters"""
    
    def process_request(self, request):
        # Check for referral code in URL (?ref=ABC123)
        ref_code = request.GET.get('ref')
        
        if ref_code:
            try:
                # Validate affiliate code
                affiliate = AffiliateProfile.objects.get(
                    affiliate_code=ref_code,
                    status='active'
                )
                
                # Store in session (30 days cookie)
                request.session['affiliate_ref'] = ref_code
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                
                # Track the referral click
                referral = AffiliateReferral.objects.create(
                    affiliate=affiliate,
                    referral_code=ref_code,
                    ip_address=self.get_client_ip(request),
                    landing_page=request.build_absolute_uri()
                )
                
                # Associate user if logged in
                if request.user.is_authenticated:
                    referral.referred_user = request.user
                    referral.save()
                
                # Update total referrals count
                affiliate.total_referrals += 1
                affiliate.save()
                
            except AffiliateProfile.DoesNotExist:
                pass  # Invalid code, ignore
        
        # Update existing referrals if user just logged in
        elif request.user.is_authenticated and 'affiliate_ref' in request.session:
            ref_code = request.session['affiliate_ref']
            # Update referrals with no user but matching IP and code
            AffiliateReferral.objects.filter(
                referral_code=ref_code,
                referred_user__isnull=True,
                ip_address=self.get_client_ip(request)
            ).update(referred_user=request.user)
        
        return None
    
    def get_client_ip(self, request):
        """Get real IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
